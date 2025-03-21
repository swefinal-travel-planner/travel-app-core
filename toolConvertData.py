import json
from constant.data import locations 

with open("locations.jsonl", "w", encoding="utf-8") as f:
    for location in locations:
        message = {
            "messages": [
                {"role": "system", "content": "Bạn là một trợ lý AI chuyên về thông tin du lịch."},
                {"role": "user", "content": f"Hãy cung cấp thông tin về địa điểm: {location['tên']}"},
                {"role": "assistant", "content": json.dumps(location, ensure_ascii=False)}
            ]
        }
        f.write(json.dumps(message, ensure_ascii=False) + "\n")

print("Dữ liệu đã được lưu vào locations.jsonl")