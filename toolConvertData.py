import json
from constant.data import locations 

with open("locations.jsonl", "w", encoding="utf-8") as f:
    for location in locations:
        message = {
            "messages": [
                {"role": "system", "content": f"Đây là thông tin về địa điểm: {location['tên']}: {json.dumps(location, ensure_ascii=False)}"},
                # {"role": "user", "content": f"Hãy cung cấp thông tin về địa điểm: {location['tên']}"},
                {"role": "assistant", "content": "Đã hiểu"}
            ]
        }
        f.write(json.dumps(message, ensure_ascii=False) + "\n")

print("Dữ liệu đã được lưu vào locations.jsonl")