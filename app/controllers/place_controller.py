from app.services.place_service import PlaceService
from injector import inject

class PlaceController:
    @inject
    def __init__(self, place_service: PlaceService):
        self.place_service = place_service

    def get_places(self):
        data = self.place_service.embed_text('Hello World')
        return str(data)