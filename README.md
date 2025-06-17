# 🤖 KahootAI Bot

This project is an experimental **AI-powered Kahoot bot** that uses a language model (via OpenRouter API) to automatically join Kahoot games and attempt to answer questions based on the provided choices.

> ⚠️ **This project is for educational and research purposes only.**  
> Using bots on platforms like Kahoot may violate their Terms of Service.  
> The author is not responsible for any misuse of this tool.

---

## 🚀 Features

- Automatic login to a Kahoot game using a PIN and nickname.
- Real-time question and choices extraction.
- OpenRouter API integration to select the best answer using an AI model.
- Automatically selects and clicks the chosen answer.

---

## 🔧 Requirements

- Python 3.8+
- Google Chrome + ChromeDriver
- OpenRouter API key (https://openrouter.ai)

---

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/DevA-R-K/Kahoot-AI.git
   cd kahoot-ai-bot
2. Make sure you have Python 3.8 or later installed.
3. Install Python dependencies
- pip install -r requirements.txt

## 💡 How to Run
Once everything is set up:
python kahootAI.py
You will be prompted to enter:

✅ Your OpenRouter API key

✅ The Kahoot game PIN

✅ Your nickname

The bot will then:

Join the game

Detect questions and answer options

Ask the OpenRouter AI for the correct answer

Automatically click the answer in the Kahoot interface
