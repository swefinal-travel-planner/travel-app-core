import json
import aiohttp
import asyncio
from injector import inject
from typing import Tuple
from app.models.distance_entry import DistanceEntry
from app.models.language import Language
from app.models.place_with_location import PlaceWithLocation
from app.services.place_service import PlaceService
from aiolimiter import AsyncLimiter
import threading
import time

MAX_BATCH = 12
CACHE_FILE = "./constant/distance_cache.json"

def load_distance_cache():
    distance_cache = {}
    try:
        with open(CACHE_FILE, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                entry = DistanceEntry.from_dict(data)
                key = tuple(sorted([entry.source_id, entry.destination_id]))
                if key not in distance_cache and entry.distance != 0:
                    distance_cache[key] = entry

        # Save the cleaned cache back to the file
        try:
            with open(CACHE_FILE, "w") as f:
                for entry in distance_cache.values():
                    json.dump(entry.to_dict(), f)
                    f.write("\n")
            print(f"Successfully saved {len(distance_cache)} unique entries to cache.")
        except IOError as e:
            print(f"Failed to save cache file: {e}")

        print(f"Loaded {len(distance_cache)} unique entries from cache.")
    except FileNotFoundError:
        print("No cache file found.")
    return distance_cache

class DistanceMatrixService:
    @inject
    def __init__(self, mapbox_api_key, place_service: PlaceService):
        self.__api_key = mapbox_api_key
        self.__base_url = "https://api.mapbox.com/directions-matrix/v1/mapbox"
        self.__distance_cache = load_distance_cache() or {}  # Đảm bảo luôn là danh sách
        self.__place_service = place_service
        schedule_reload_cache(self, 60*60)  # Tự động reload cache mỗi 1 giờ

    @property
    def limiter(self):
        loop = asyncio.get_event_loop()
        if not hasattr(self, "_limiters"):
            self._limiters = {}
        if loop not in self._limiters:
            self._limiters[loop] = AsyncLimiter(55, 60)
        return self._limiters[loop]

    def _build_url(self, profile: str, coords: list[Tuple[float, float]]) -> str:

        return f"{self.__base_url}/{profile}/" + ";".join([f"{long},{lat}" for long,lat in coords])
    
    async def call_matrix(self, all_coords, source_ids, dest_ids, profile="driving"):
        id_to_index = {f"{long},{lat}": idx for idx, (long, lat) in enumerate(all_coords)}
        source_idx = [id_to_index[src_id] for src_id in source_ids]
        dest_idx = [id_to_index[id] for id in dest_ids]

        url = self._build_url(profile, all_coords)
        params = {
            "sources": ";".join(map(str, source_idx)),
            "destinations": ";".join(map(str, dest_idx)),
            "access_token": self.__api_key,
            "annotations": "distance"
        }

        async with self.limiter:
            async with aiohttp.ClientSession() as session:
                for attempt in range(3):  # thử lại tối đa 3 lần
                    try:
                        async with session.get(url, params=params) as resp:
                            resp.raise_for_status()
                            data = await resp.json()
                            if data.get("message") and data.get("message") == "InvalidInput":
                                raise ValueError(f"API error: {data.get('message', 'InvalidInput')}")
                            distances = data.get("distances")
                            return distances
                    except aiohttp.ClientResponseError as e:
                        if e.status == 429:
                            print("Hit rate limit, retrying after delay...")
                            await asyncio.sleep(10)  # chờ 10 giây rồi thử lại
                            continue
                        raise ValueError(f"HTTP error occurred: {e}")
                    except aiohttp.ClientError as e:
                        raise ValueError(f"Request error occurred: {e}")
                raise ValueError("Too many requests: exceeded retry limit")
    
    async def calculate_all_pairs(self, source: list[PlaceWithLocation], destination: list[PlaceWithLocation]):
        # Tạo danh sách các cặp (src, dest) chưa có trong cache
        pairs_to_process = []
        for src in source:
            for dest in destination:
                if self.find_distance(src.id, dest.id) is not None:
                    continue
                pairs_to_process.append((src, dest))

        # Chia batch cho source và destination để đảm bảo mọi kết hợp đều được xử lý
        src_batches = [source[i:i+MAX_BATCH] for i in range(0, len(source), MAX_BATCH)]
        dest_batches = [destination[j:j+MAX_BATCH] for j in range(0, len(destination), MAX_BATCH)]

        for src_batch in src_batches:
            for dest_batch in dest_batches:
                # Lọc ra các cặp thực sự cần xử lý trong batch này
                batch_pairs = [
                    (src, dest)
                    for src in src_batch
                    for dest in dest_batch
                    if (src, dest) in pairs_to_process
                ]
                if not batch_pairs:
                    continue
                # Lấy unique src và dest trong batch này (dựa trên id)
                batch_src = []
                batch_dest = []
                src_ids = set()
                dest_ids = set()
                for src, _ in batch_pairs:
                    if src.id not in src_ids:
                        batch_src.append(src)
                        src_ids.add(src.id)
                for _, dest in batch_pairs:
                    if dest.id not in dest_ids:
                        batch_dest.append(dest)
                        dest_ids.add(dest.id)
                # Bỏ qua batch nếu chỉ có 1 source hoặc 1 destination
                if len(batch_src) < 2 or len(batch_dest) < 2:
                    batch_src.append(batch_src[0])
                await self._process_batch(batch_src, batch_dest)

    async def _process_batch(self, pending_src, pending_dest):
        batch_src_coords = [(s.long, s.lat) for s in pending_src]
        batch_dest_coords = [(d.long, d.lat) for d in pending_dest]
        batch_coords = batch_src_coords + batch_dest_coords

        try:
            distances = await self.call_matrix(
                batch_coords,
                [f"{s.long},{s.lat}" for s in pending_src],
                [f"{d.long},{d.lat}" for d in pending_dest]
            )

        except ValueError as e:
            print(f"Error calling call_matrix: {e}")
            raise 

        for ii, row in enumerate(distances):
            for jj, dist in enumerate(row):
                if dist == 0:
                    continue
                src_obj = pending_src[ii]
                dest_obj = pending_dest[jj]
                entry = DistanceEntry(
                    source_id=src_obj.id,
                    destination_id=dest_obj.id,
                    distance=dist
                )
                key = tuple(sorted([entry.source_id, entry.destination_id]))
                if key not in self.__distance_cache:
                    self.__distance_cache[key] = entry
                    self.append_distance_to_file(entry)

    def append_distance_to_file(self, entry: DistanceEntry):
        with open(CACHE_FILE, "a") as f:
            json.dump(entry.to_dict(), f)
            f.write("\n")

    def find_distance(self, source_id: str, destination_id: str) -> float:
        key = tuple(sorted([source_id, destination_id]))
        entry = self.__distance_cache.get(key)
        return entry.distance if entry else None
    
    def get_distance_time(self, list_place_id: list[str]):
        results = []
        missing_pairs = []
        for i in range(len(list_place_id) - 1):
            src_id = list_place_id[i]
            dest_id = list_place_id[i + 1]
            dist = self.find_distance(src_id, dest_id)
            if dist is not None:
                distance_km = round(dist / 1000, 2)  # làm tròn 2 chữ số
                time_min = round((distance_km / 20) * 60, 1)  # làm tròn 1 chữ số
                results.append({
                    "source_id": src_id,
                    "destination_id": dest_id,
                    "distance": distance_km,
                    "time": time_min
                })
            else:
                missing_pairs.append((src_id, dest_id))
                results.append({
                    "source_id": src_id,
                    "destination_id": dest_id,
                    "distance": 0,
                    "time": 0
                })

        if missing_pairs:
            id_to_place = {}
            for pid in set([pid for pair in missing_pairs for pid in pair]):
                place = self.__place_service.get_place_by_id(pid, Language.EN)

                id_to_place[pid] = PlaceWithLocation(
                    id=place["id"],
                    long=place["location"]["long"],
                    lat=place["location"]["lat"],
                    score=0
                )

            src_places = [id_to_place[src] for src, _ in missing_pairs]
            dest_places = [id_to_place[dest] for _, dest in missing_pairs]
            src_places = list({p.id: p for p in src_places}.values())
            dest_places = list({p.id: p for p in dest_places}.values())

            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            if loop.is_running():
                coro = self.calculate_all_pairs(src_places, dest_places)
                asyncio.ensure_future(coro)
            else:
                loop.run_until_complete(self.calculate_all_pairs(src_places, dest_places))

            # Update results with newly calculated distances
            for item in results:
                if item["distance"] == 0:
                    dist = self.find_distance(item["source_id"], item["destination_id"])
                    if dist is not None:
                        distance_km = round(dist / 1000, 2)
                        time_min = round((distance_km / 30) * 60, 1)
                        item["distance"] = distance_km
                        item["time"] = time_min

        return results

def schedule_reload_cache(service_instance,interval_seconds: int = 600):
    def reload_loop():
        while True:
            try:
                service_instance._DistanceMatrixService__distance_cache = load_distance_cache()
                print("Distance cache reloaded.")
            except Exception as e:
                print(f"Error reloading distance cache: {e}")
            time.sleep(interval_seconds)
    thread = threading.Thread(target=reload_loop, daemon=True)
    thread.start()