# 💌 Anonymous Valentines Bot

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)
![aiogram](https://img.shields.io/badge/aiogram-2.x-green.svg)
![Stars](https://img.shields.io/github/stars/stavrmoris/Anonymous_valentines-bot)

Anonymous Valentines Bot - это телеграм-бот, который позволяет пользователям анонимно отправлять валентинки друг другу.

[Read in English](README.md)

## 📚 Оглавление

- [Описание](#описание)
- [Установка](#установка)
- [Использование](#использование)
- [Лицензия](#лицензия)

## 📜 Описание

Этот код реализует телеграм-бота, который позволяет пользователям отправлять анонимные сообщения и подписываться на премиум-услуги. Основные функции включают покупку подписки, отправку анонимных сообщений и проверку статуса подписки пользователя. Бот использует библиотеку aiogram для взаимодействия с Telegram API и базу данных SQLite для хранения данных пользователей и их подписок.

## 🔧 Установка

1. **Клонировать репозиторий:**
    ```bash
    git clone https://github.com/stavrmoris/Anonymous_valentines-bot.git
    cd Anonymous_valentines-bot
    ```

2. **Создать виртуальное окружение и активировать его:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # на Windows используйте `venv\Scripts\activate`
    ```

3. **Установить необходимые зависимости:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Создать конфигурационный файл `.env` и добавить ваши данные:**
    ```
    TELEGRAM_TOKEN=ваш_токен_телеграм_бота
    ```

## 🚀 Использование

1. **Запустить бота:**
    ```bash
    python bot.py
    ```

2. **Взаимодействовать с ботом:**
   - Откройте Telegram и найдите вашего бота по его имени.
   - Отправьте команду `/start`, чтобы начать использовать бота.
   - Следуйте инструкциям для отправки анонимных валентинок.

## 📄 Лицензия

Этот проект лицензирован по лицензии MIT. Подробнее см. файл [LICENSE](LICENSE).
