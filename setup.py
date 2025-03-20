from flask import Flask, jsonify, request
from flask_cors import CORS
from data import locations
from prompt import pre_prompt, post_prompt, prompt1, prompt2, prompt3, prompt4, prompt5, prompt6
import google.generativeai as genai
import json
from models.UserPreferences import UserPreferences
from utils.getResponse import get_ai_response
from dotenv import load_dotenv


def createApp():
    app = Flask(__name__)
    cors = CORS(app)
    app.config['CORS_HEADER'] = 'Content-Type'
    load_dotenv()

    @app.route('/generate', methods=['POST'])
    def generate():
        conversation_history = []
        try:
            data = request.json
            # Create a new user preferences
            user_prefs = UserPreferences(
                num_days=data["days"],
                budget=data["budget"],
                slots=data["slots"],
                location_attributes=data["location_attributes"],
                food_attributes=data["food_attributes"],
                special_requirements=data["special_requirements"],
                medical_conditions=data["medical_conditions"]
            )
            key = os.getenv("api_key")
            # setup model
            genai.configure(api_key="")
            model = genai.GenerativeModel("gemini-2.0-flash-exp")

            #setup data string
            locations_string = json.dumps(locations, ensure_ascii=False, indent=2)

            #first call API to filter locations
            initial_prompt = prompt1 + " " + user_prefs.to_string() + " .Đây là danh sách địa điểm: "+ locations_string
            conversation_history.append({"role": "user", "content": initial_prompt})

            try:
                selected_ids_v1 = get_ai_response(model,conversation_history)

                if len(selected_ids_v1) == 0 or selected_ids_v1[0] == 0:
                    return jsonify({"response": "no location"}), 400
                
                # Append conversation history for debugging and user review
                conversation_history.append({"role": "model", "content": json.dumps(selected_ids_v1, ensure_ascii=False)})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
            
            #second call API ro check data from the first call
            validation_prompt = prompt2
            conversation_history.append({"role": "user", "content": validation_prompt})
            
            try:
                selected_ids_v2 = get_ai_response(model,conversation_history)
                
                # Append conversation history for debugging and user review
                conversation_history.append({"role": "model", "content": json.dumps(selected_ids_v2, ensure_ascii=False)})
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500

            # third call API to arrange location reasonably
            arrange_prompt = prompt3
            conversation_history.append({"role": "user", "content": arrange_prompt})

            try:
                selected_ids_v3 = get_ai_response(model, conversation_history)
                
                # Append conversation history for debugging and user review
                conversation_history.append({"role": "model", "content": json.dumps(selected_ids_v3, ensure_ascii=False)})
                
                return jsonify({"response": conversation_history}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    return app
