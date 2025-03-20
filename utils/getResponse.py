import json


def get_ai_response(model, history):
    try:
        prompt = "\n".join(
                [f'{msg["role"]}: {msg["content"]}' for msg in history]
            )
        response = model.generate_content(prompt)
        response_data = response.to_dict()
        
        raw_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        clean_text = raw_text.replace("```json\n", "").replace("```", "").replace("model: ","").strip()
        return json.loads(clean_text)
    except Exception as e:
        raise Exception(f"Lỗi model: {str(e)}")