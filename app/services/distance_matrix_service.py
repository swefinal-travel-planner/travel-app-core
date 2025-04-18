from injector import inject
import requests

class DistanceMatrixService:
    @inject
    def __init__(self, mapbox_api_key):
        self.__api_key = mapbox_api_key
        self.__base_url = "https://api.mapbox.com/directions-matrix/v1/mapbox"

    def calculate_distance_matrix(self, origins, destinations, profile="driving"):
        """
        Calculate the distance matrix using Mapbox API.

        :param origins: List of origin coordinates as "longitude,latitude".
        :param destinations: List of destination coordinates as "longitude,latitude".
        :param profile: Profile for routing (e.g., 'driving', 'walking', 'cycling').
        :return: Distance matrix response from Mapbox API.
        """
        try:
            coordinates = ";".join(origins + destinations)
            url = f"{self.__base_url}/{profile}/{coordinates}"
            sources = ";".join(map(str, range(len(origins))))
            destinations_indices = range(len(origins), len(origins) + len(destinations))
            destinations = ";".join(map(str, destinations_indices))
            params = {
                "sources": sources,
                "destinations": destinations,
                "access_token": self.__api_key,
                "annotations": "distance"
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error calculating distance matrix: {e}")
            return None
