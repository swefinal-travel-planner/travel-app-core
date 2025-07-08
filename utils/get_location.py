import requests
from config.config import Config
from constant.supported_district_city import supported_districts

def get_address_by_location(longitude, latitude):
    # dùng mapbox api để lấy địa chỉ
    mapbox_access_token = Config.MAPBOX_API_KEY
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{longitude},{latitude}.json?access_token={mapbox_access_token}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["features"]:
            return data["features"][0]["place_name"]
    return None

def get_district_by_address(address):
    # dùng mapbox api để lấy quận/huyện
    openai_api_key = Config.OPENAI_API_KEY
    prompt = f"Đây là địa chỉ của 1 địa điểm tại tp Hồ Chí Minh: Địa chỉ: {address}\nHãy cho biết địa chỉ này thuộc quận/huyện nào ở Hồ Chí Minh, chỉ trả về tên quận/huyện bằng tiếng anh.ví dụ : District 1, Hoc Mon District. Không giải thích gì thêm mà chỉ trả về tên quận/huyện duy nhất. chỉ được trả về các quận được đưa ra dưới đây: {', '.join(supported_districts)}"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4.1-mini-2025-04-14",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 20,
        "temperature": 0
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    else:
        return None