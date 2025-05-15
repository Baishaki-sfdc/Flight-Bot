# ✈️ AirMate - AI-Powered Flight Booking Assistant

**AirMate** is a conversational flight booking assistant built with **Streamlit** and powered by **OpenRouter's GPT API**. It guides users through selecting flight details, validates inputs, and displays available flight options—all in a user-friendly chat interface.

---

## 🚀 Features

- 💬 Conversational UI built with **Streamlit**
- 🧠 GPT-powered assistant via **OpenRouter**
- ✅ Real-time **input validation** (cities, dates, seating class)
- ✈️ Displays dynamic **flight options**
- 🎉 Simulated booking with **confirmation**
- 🎨 Custom dark-themed styling with CSS
- ⚙️ Devcontainer support for easy deployment

---

## 📁 Project Structure

```text
baishaki-sfdc-flight-bot/
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── app/
│   ├── __init__.py             # App package initializer
│   └── airmate_app.py          # Main Streamlit app
├── assets/
│   └── styles.css              # Custom CSS for UI styling
├── .devcontainer/
│   └── devcontainer.json       # VSCode devcontainer configuration
└── .streamlit/
    └── secrets.toml            # Environment secrets (API keys)


🛠️ Setup Instructions

git clone https://github.com/yourusername/baishaki-sfdc-flight-bot.git
cd baishaki-sfdc-flight-bot


