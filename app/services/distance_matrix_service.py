import json
import aiohttp
from injector import inject
from typing import Tuple
from app.models.distance_entry import DistanceEntry
from app.models.place_with_location import PlaceWithLocation
import asyncio

MAX_BATCH = 12
CACHE_FILE = "./constant/distance_cache.json"

def load_distance_cache():
    distance_cache = []
    try:
        with open(CACHE_FILE, "r") as f:
            check_esxist = False
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                entry = DistanceEntry.from_dict(data)
                for existing_entry in distance_cache:
                    if (existing_entry.source_id == entry.source_id and existing_entry.destination_id == entry.destination_id) or \
                       (existing_entry.source_id == entry.destination_id and existing_entry.destination_id == entry.source_id):
                        check_esxist = True
                        break
                if check_esxist or entry.distance == 0:
                    check_esxist = False
                else:
                    distance_cache.append(entry)

        # Save the cleaned cache back to the file
        try:
            with open(CACHE_FILE, "w") as f:
                for entry in distance_cache:
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
    def __init__(self, mapbox_api_key):
        self.__api_key = mapbox_api_key
        self.__base_url = "https://api.mapbox.com/directions-matrix/v1/mapbox"
        self.__distance_cache = load_distance_cache() or []  # Đảm bảo luôn là danh sách

    def _build_url(self, profile: str, coords: list[Tuple[float, float]]) -> str:

        return f"{self.__base_url}/{profile}/" + ";".join([f"{long},{lat}" for long,lat in coords])
    
    async def call_matrix(self, all_coords: list[Tuple[float, float]], source_ids: list[str], dest_ids: list[str], profile="driving"):
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

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    # Kiểm tra lỗi từ API
                    if data.get("message") and data.get("message") == "InvalidInput":
                        raise ValueError(f"API error: {data.get('message', 'InvalidInput')}")
                    distances = data.get("distances")
                    return distances
            except aiohttp.ClientResponseError as e:
                raise ValueError(f"HTTP error occurred: {e}")
            except aiohttp.ClientError as e:
                raise ValueError(f"Request error occurred: {e}")
    
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
            await asyncio.sleep(3)
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
                self.__distance_cache.append(entry)
                self.append_distance_to_file(entry)

    def append_distance_to_file(self, entry: DistanceEntry):
        with open(CACHE_FILE, "a") as f:
            json.dump(entry.to_dict(), f)
            f.write("\n")

    def find_distance(self, source_id: str, destination_id: str) -> float:
        for entry in self.__distance_cache:
            if entry.source_id == source_id and entry.destination_id == destination_id:
                return entry.distance
            if entry.source_id == destination_id and entry.destination_id == source_id:
                return entry.distance
        return None

