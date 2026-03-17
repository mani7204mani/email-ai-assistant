# 📧 AI Email Summarizer & Reply Generator

> An AI-powered Gmail assistant that reads your unread emails, generates smart summaries, and suggests professional reply options — all in one click.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.42-red?logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-0.3-green)
![Groq](https://img.shields.io/badge/LLM-Groq%20LLaMA3-orange)
![Gmail API](https://img.shields.io/badge/Gmail-API-red?logo=gmail)
![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)

---

## 🚀 Live Demo

👉 **[Try it here → email-ai-assistant.streamlit.app](https://email-ai-assistant.streamlit.app)**

> When Google shows a warning screen, click **Advanced → Go to email-ai-assistant.streamlit.app (unsafe)**  
> This is normal for unverified personal projects and is completely safe.

---

## 📸 Features

| Feature | Description |
|---|---|
| 🔐 Gmail OAuth Login | Each user logs in with their own Gmail securely |
| 📋 AI Email Summary | Summarizes email in 2-3 sentences with priority level |
| ✍️ Smart Reply Generator | Generates 2 reply options — brief and detailed |
| ✏️ Edit Before Send | Edit the AI-generated reply before sending |
| 👁️ Preview Email | See full formatted email with signature before sending |
| 📤 One-Click Send | Send directly from the app without opening Gmail |
| ✒️ Custom Signature | Set your name, title, company, phone, LinkedIn once — added to every reply |
| 🚪 Logout | Securely logout anytime |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit |
| **AI / LLM** | LangChain + Groq (LLaMA 3.3 70B) |
| **Email Integration** | Gmail API (OAuth 2.0) |
| **Deployment** | Streamlit Cloud |
| **Language** | Python 3.11 |

---

## 🏗️ Architecture
```
User (Browser)
      ↓
Streamlit App (Frontend)
      ↓              ↓
Gmail API        LangChain + Groq LLM
      ↓              ↓
  Fetch Emails   Summarize & Generate Replies
      ↓              ↓
         Result Card (Preview + Send)
      ↓
  Sent via Gmail API
```

---

## ⚙️ How It Works

1. User logs in with their Gmail account via OAuth 2.0
2. App fetches unread emails from inbox
3. User clicks **"Generate Summary"** → LLaMA 3.3 analyzes and summarizes the email
4. User clicks **"Generate Replies"** → LLM generates 2 professional reply options
5. User edits the reply if needed → previews the full formatted email
6. User clicks **"Send"** → email is sent directly via Gmail API with signature

---

## 🚀 Run Locally

### Prerequisites
- Python 3.11+
- Gmail API credentials (Google Cloud Console)
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Installation
```bash
# Clone the repo
git clone https://github.com/mani7204mani/email-ai-assistant.git
cd email-ai-assistant

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### Setup Secrets

Create `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your_groq_api_key"
REDIRECT_URI = "http://localhost:8501"

[google_credentials]
client_id = "your_google_client_id"
client_secret = "your_google_client_secret"
redirect_uri = "http://localhost:8501"
```

### Run
```bash
streamlit run app.py
```

---

## 📁 Project Structure
```
email-ai-assistant/
├── app.py              # Main Streamlit frontend
├── gmail_helper.py     # Gmail API integration (fetch + send)
├── ai_engine.py        # LangChain + Groq LLM logic
├── requirements.txt    # Python dependencies
├── .python-version     # Python 3.11 pinned
├── .gitignore
└── .streamlit/
    └── secrets.toml    # API keys (not pushed to GitHub)
```

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key |
| `REDIRECT_URI` | OAuth redirect URI |
| `google_credentials.client_id` | Google OAuth client ID |
| `google_credentials.client_secret` | Google OAuth client secret |

---

## 📝 How to Use the Live App

1. Go to **[email-ai-assistant.streamlit.app](https://email-ai-assistant.streamlit.app)**
2. Click **"Login with Gmail"** → opens in new tab
3. Select your Google account → click **Advanced → Go to app (unsafe)**
4. Allow Gmail permissions
5. Set your email signature (name, title, company)
6. Your unread emails will load automatically
7. Click **Generate Summary** or **Generate Replies** on any email
8. Edit the reply → Preview → Send!

---

## 🙋 About the Developer

Built by **Mani Reddy** as part of a portfolio project while transitioning into AI Engineering.

- 🔗 [LinkedIn](https://linkedin.com/in/yourprofile)
- 💻 [GitHub](https://github.com/mani7204mani)

---

## 📄 License

This project is for educational and portfolio purposes.

---

⭐ **If you found this useful, give it a star!**
