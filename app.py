import requests
from flask import Flask, request, jsonify
from pymongo import MongoClient
from twilio.rest import Client
import google.generativeai as genai
from datetime import datetime
import os
from dotenv import load_dotenv
from datetime import datetime, UTC
import pandas as pd
from io import StringIO


load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client_mongo = MongoClient(MONGO_URI)
db = client_mongo["chatbot_db"]
chat_collection = db["chats"]
user_collection = db["users"]

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

model = None
try:
    model = genai.GenerativeModel(model_name='gemini-2.0-flash-001')
except Exception as e:
    print(f"Error initializing gemini-pro: {e}")
    try:
        model = genai.GenerativeModel(model_name='models/gemini-pro')
    except Exception as e2:
        print(f"Error initializing models/gemini-pro: {e2}")
        try:
            model = genai.GenerativeModel(model_name='gemini-pro', api_version='v1')
        except Exception as e3:
            print(f"Error initializing gemini-pro with v1: {e3}")
            raise

system_prompt = "You are a helpful and professional Data Science expert chatbot."

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_data = request.form
    user_msg = incoming_data.get("Body")
    from_number = incoming_data.get("From")
    num_media = int(incoming_data.get("NumMedia", 0))

    user_data = user_collection.find_one({"from": from_number})
    if not user_data:
        user_data = {"from": from_number}
        user_collection.insert_one(user_data)

    if user_msg.lower().startswith("my name is"):
        name = user_msg.split("is", 1)[1].strip()
        user_data["name"] = name
        user_collection.update_one({"from": from_number}, {"$set": {"name": name}})
        bot_msg = f"Got it, {name}! I'll remember your name from now on."
    else:
        name = user_data.get("name", "there")
        bot_msg = f"Hello {name}, how can I help you today?"

    chat_collection.insert_one({
        "from": from_number,
        "message": user_msg if user_msg else "[media]",
        "sender": "user",
        "timestamp": datetime.now(UTC)
    })

    if num_media > 0:
        media_url = incoming_data.get("MediaUrl0")
        content_type = incoming_data.get("MediaContentType0")

        if "csv" in content_type:
            try:
                response = requests.get(media_url, auth=(TWILIO_SID, TWILIO_AUTH_TOKEN))
                csv_data = response.content.decode('utf-8')
                df = pd.read_csv(StringIO(csv_data))

                summary = df.describe(include='all').to_string()
                null_info = df.isnull().sum().to_string()
                insights = f"CSV Summary:\n{summary}\n\nMissing Values:\n{null_info}"

                chat_collection.insert_one({
                    "from": from_number,
                    "message": insights,
                    "sender": "bot",
                    "timestamp": datetime.now(UTC)
                })

                twilio_client.messages.create(
                    body=insights[:1599],
                    from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
                    to=from_number
                )
            except Exception as e:
                error_msg = f"Error analyzing CSV: {e}"
                twilio_client.messages.create(
                    body=error_msg,
                    from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
                    to=from_number
                )
        else:
            twilio_client.messages.create(
                body="Please send a CSV file only.",
                from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
                to=from_number
            )
    else:
        if model:
            chat_history = chat_collection.find({"from": from_number}).sort("timestamp", -1).limit(5)
            chat_history_list = list(chat_history)[::-1]

            conversation_context = system_prompt + "\n"
            for msg in chat_history_list:
                role = "User" if msg["sender"] == "user" else "Bot"
                conversation_context += f"{role}: {msg['message']}\n"
            conversation_context += f"User: {user_msg}\nBot:"

            try:
                response = model.generate_content(conversation_context + " Please answer in under 200 words.")
                bot_msg = response.text if response.text else "Sorry, I couldn't generate a response."
            except Exception as e:
                bot_msg = f"Error generating response: {e}"

            chat_collection.insert_one({
                "from": from_number,
                "message": bot_msg,
                "sender": "bot",
                "timestamp": datetime.now(UTC)
            })

            try:
                twilio_client.messages.create(
                    body=bot_msg[:1599],
                    from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
                    to=from_number
                )
            except Exception as e:
                print(f"Error sending Twilio message: {e}")
        else:
            print("Gemini model not initialized.")

    return "OK", 200

@app.route('/test', methods=['GET'])
def test():
    test_message = request.args.get("msg", "my freinds are so exicted fo this project. one of my freind name is neeraj?")

    if model:
        prompt_with_context = f"{system_prompt} User: {test_message}"
        try:
            response = model.generate_content(prompt_with_context)
            bot_response = response.text if response.text else "Sorry, I couldn't generate a response for the test."
            return jsonify({"response": bot_response})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Gemini model not initialized."}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
