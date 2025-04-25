# 💬 WhatsApp Data Science AI Agent 🤖📊

An AI-powered WhatsApp chatbot built with **LangChain**, **Flask**, **Twilio**, and **Google Gemini Pro**, enabling users to interact with AI via chat or by sending CSV files. Get instant insights like data summaries, null value checks, and more – all within WhatsApp!

---

## 🚀 Key Features

✅ **CSV Insights via WhatsApp**  
- Upload `.csv` files directly in chat  
- Receive:  
  - Descriptive statistics (mean, median, mode, etc.)  
  - Null value analysis  

🧠 **Memory-Based Conversational AI**  
- Remembers previous chats (MongoDB-backed)  
- Handles context-aware replies  

🔐 **Secure**  
- Uses `.env` file for storing sensitive credentials  

📦 **Lightweight & Modular**  
- Easily extendable Flask-based architecture  

---

## 🛠️ Tech Stack

| Component     | Tech Used                      |
|---------------|-------------------------------|
| Backend       | Python (Flask)                |
| AI Framework  | LangChain + Google Gemini Pro |
| Messaging     | Twilio WhatsApp API           |
| Data Handling | Pandas                        |
| Memory Store  | MongoDB                       |

---

## 📦 Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Bharatgwl/Whatsapp-DS-AI-agent-using-langChain-.git

cd Whatsapp-DS-AI-agent-using-langChain-
```


### 2. Set up virtual environment (Windows)
```
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Create a .env file in the root directory
```
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=whatsapp:+14155238886
GEMINI_API_KEY=your_gemini_api_key
MONGO_URI=your_mongodb_connection_string
```


## 🌐 Deployment
### Run your Flask server locally
```
python app.py
```

### Expose server using Ngrok
```
ngrok http 5000
```


## Update your Twilio Webhook
Go to Twilio Console

Set the Webhook to: https://your-ngrok-url/webhook

## 📁 Project Structure
```
.
├── app.py                # Main Flask app
├── .env                  # Environment variables (not committed)
├── .gitignore            # Files to ignore in Git
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```
# Project documentation

### 🙌 Contributing
Pull requests are welcome! Feel free to fork the repo, improve it, and create a PR.

### ✨ Author
Developed with ❤️ by Bharat

### 📃 License
This project is licensed under the MIT License.
```bash