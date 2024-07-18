# 💌 Anonymous Valentines Bot

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)
![aiogram](https://img.shields.io/badge/aiogram-3.x-green.svg)
![Stars](https://img.shields.io/github/stars/stavrmoris/Anonymous_valentines-bot)

Anonymous Valentines Bot is a telegram bot that allows users to anonymously send valentines to each other.

[Читать на русском](README_RU.md)

## 📚 Table of Contents

- [Description](#-description)
- [Installation](#-installation)
- [Usage](#-usage)
- [License](#-license)

## 📜 Description

This code implements a Telegram bot that allows users to send anonymous messages and subscribe to premium services. The main functions include purchasing a subscription, sending anonymous messages, and checking a user's subscription status. The bot uses the aiogram library to interact with the Telegram API and an SQLite database to store user data and their subscriptions.

## 🔧 Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/stavrmoris/Anonymous_valentines-bot.git
    cd Anonymous_valentines-bot
    ```

2. **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # on Windows use `venv\Scripts\activate`
    ```

3. **Install the necessary dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Open a configuration file `.env` and add your data:**
    ```
    TELEGRAM_TOKEN=your_telegram_bot_token
    ```

5. **Open a configuration file `config_reader.py` and add your data:**
    ```
    PAYMENTS_TOKEN = '12345:your_payments_token:54321'
    ```

5. **Open a main bot script `bot.py` and add your data:**
    ```
    bot_name = 'your bot name'
    ```

## 🚀 Usage

1. **Run the bot:**
    ```bash
    python bot.py
    ```

2. **Interact with the bot:**
   - Open Telegram and find your bot by its name.
   - Send the command `/start` to start using the bot.
   - Follow the instructions to send anonymous valentines.
  

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
