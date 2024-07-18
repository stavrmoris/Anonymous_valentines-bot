import re
import asyncio
import logging
import sqlite3

from datetime import datetime, timedelta
from aiogram.enums import ContentType
from config_reader import config, PAYMENTS_TOKEN
from aiogram.types import Message
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession

# Database connections
connection = sqlite3.connect('data.db')
cursor = connection.cursor()

connection2 = sqlite3.connect('all_users.db')
cursor2 = connection2.cursor()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize the bot and dispatcher
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

# Define subscription price in kopecks (rubles)
PRICE = types.LabeledPrice(label="1-month subscription", amount=169 * 100)

# Global variables for user interaction
user_id = 0
user2 = 0
name = "undefined"
user_only = False
canWrite = False

# Function to convert date to integer
def date_integer(dt_time):
    return 10000 * dt_time.year + 100 * dt_time.month + dt_time.day

# Async function to replace "@" in string
async def ChangeStr(string):
    return str(string).replace('@', '')

# Callback for handling subscription purchase
@dp.callback_query(F.data == "buy")
async def buy(message: types.Message):
    if PAYMENTS_TOKEN.split(':')[1] == 'TEST':
        await message.answer("Test payment!!!")

    await bot.send_invoice(message.from_user.id,
                           title="Bot Subscription",
                           description="🤖 Activate bot subscription for 30 days",
                           provider_token=PAYMENTS_TOKEN,
                           currency="rub",
                           photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
                           photo_width=416,
                           photo_height=234,
                           photo_size=416,
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter='fount-of-discounts',
                           payload="test-invoice-payload")

# Pre-checkout query handler
@dp.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

# Handler for successful payment
@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    print("SUCCESSFUL PAYMENT:")

    print(f"ID of premium buyer: {message.from_user.id}")
    cursor.execute('INSERT INTO Users (user, date) VALUES (?, ?)',
                   (f'{message.from_user.id}', date_integer(datetime.now() + timedelta(days=30))))
    connection.commit()

    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} = {v}")

    await bot.send_message(message.chat.id,
                           f"💵 Payment of {message.successful_payment.total_amount // 100} {message.successful_payment.currency} was successful! Thank you for using our service 🥰 !!!")

# Command start handler with deep link
@dp.message(CommandStart(deep_link=True, magic=F.args.regexp(re.compile(r'user_(\d+)'))))
async def cmd_start_book(message: Message, command: CommandObject):
    global user_id
    global canWrite
    global user2
    global name

    name = message.from_user.username
    user2 = message.from_user.id
    user_id = command.args.split("_")[1]
    await message.answer(f"✉️ Please write your message:")
    canWrite = True

# General start command handler
@dp.message(CommandStart())
@dp.message(F.text.lower() == "📭 start over")
async def process_start_command(message: types.Message):
    cursor2.execute("SELECT * FROM users WHERE id = ?", (message.from_user.id,))
    results = cursor2.fetchone()

    if not results:
        cursor2.execute('INSERT INTO Users (id, username) VALUES (?, ?)',
                   (f'{message.from_user.id}', message.from_user.username))
        connection2.commit()

    link = f"t.me/stavrmoris_testbot?start=user_{str(message.from_user.id)}"

    builder = ReplyKeyboardBuilder()

    builder.row(types.KeyboardButton(text="📭 Start over"))
    builder.row(types.KeyboardButton(text="🥷 Send anonymous message to user"))
    builder.row(types.KeyboardButton(text="💵 Buy subscription"))

    message_buttons = [
        [
            types.InlineKeyboardButton(
                 text="🔗 Share link",
                 switch_inline_query=f"\n💌 Send me an anonymous valentine:\n\n{link}"
            )
        ],
        [
            types.InlineKeyboardButton(
                text="🥷 Send anonymous message to user",
                callback_data="message_username"
            )
        ]
    ]

    message_builder = types.InlineKeyboardMarkup(inline_keyboard=message_buttons)

    await message.answer(
        f"❤️ Your confession link: {link}",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )
    await message.answer(
        f"📌 Pin this link in your profile or share it with friends to receive anonymous valentines!",
        reply_markup=message_builder
    )

# Handler for sending anonymous messages
@dp.message(F.text.lower() == "🥷 send anonymous message to user")
async def message_link(message: Message):
    global user_only

    user_only = True
    await message.answer(f"👱 Send any user message you want to write to.\nOr send the user's nickname. For example: @people")

# Handler for buying a subscription
@dp.message(F.text.lower() == "💵 buy subscription")
async def send_random_value(message: Message):
    global user_id
    global name
    global user2

    cursor.execute("SELECT * FROM users WHERE user = ?", (user_id,))
    results = cursor.fetchone()

    print("user_id", user_id)
    print("user2", user2)
    print(name)
    print(results)

    if (results and user_id in results) and (results[1] and datetime.strptime(str(results[1]), '%Y%m%d') >= datetime.now()):
        await message.answer(f"✅ Your subscription is still valid until {datetime.strptime(str(results[1]))}!")
    else:
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="💵 Buy",
            callback_data="buy")
        )

        await message.answer(
            f"🤖 Buy a bot subscription for 169 rubles for 30 days.",
            reply_markup=builder.as_markup()
        )

# Handler for any text message
@dp.message(F.text)
async def any_message(message: Message):
    global canWrite
    global user_only
    global user_id

    message_text = message.text

    if user_only:
        if message.forward_from is not None:
            user_id = message.forward_from.id
            print("user reply id: ", message.forward_from.id)
            await message.answer("🎉 Nickname accepted! Now write the message.")
            canWrite = True
            user_only = False
        elif message.forward_from is None:
            if message_text[0] == '@':
                message_text = message_text[1:]
                print(message_text)

            cursor2.execute("SELECT * FROM users WHERE username = ?", (message_text,))
            results = cursor2.fetchone()

            if message_text != "🥷 send anonymous message to user" or message_text != "💵 buy subscription" or message_text != "📭 start over":
                if results and results[1] == message_text:
                    user_id = results[0]
                    canWrite = True
                    user_only = False
                    await message.answer("🎉 Nickname accepted! Now write the message.")
                else:
                    await message.answer("😢 This user has never started the bot or you are providing an incorrect value. You cannot write to them.")
            else:
                user_only = False
        else:
            await message.answer(f"🤖 Sorry, but the user has blocked nickname recognition in messages.")

    elif canWrite:
        await message.answer("Your message has been successfully sent!")
        buttons = [
            [types.InlineKeyboardButton(
                text="🥸 Reply anonymously",
                callback_data=f"user_{str(message.from_user.id)}"
            )],
            [types.InlineKeyboardButton(
                text="🥷 Find out the sender",
                callback_data="premium"
            )]
        ]
        builder = types.InlineKeyboardMarkup(inline_keyboard=buttons)

        await bot.send_message(
            chat_id=user_id,
            text=f"💌 You received an anonymous message:\n\n{message.text}",
            reply_markup=builder
        )

        canWrite = False

# Callback for handling username message link
@dp.callback_query(F.data == "message_username")
async def message_link(callback: types.CallbackQuery):
    global user_only

    user_only = True
    await callback.message.edit_text(text=f"👱 Send any user message you want to write to.\nOr send the user's nickname. For example: @people")
    await callback.answer()

# Callback for handling user messages
@dp.callback_query(F.data.startswith("user_"))
async def callbacks_num(callback: types.CallbackQuery):
    global user_id
    global user2
    global canWrite
    global name

    name = callback.from_user.username
    user_id = callback.data.split("_")[1]
    user2 = callback.from_user.id
    canWrite = True
    await callback.message.edit_text("✉️ Please write your message:")

    await callback.answer()

# Callback for handling premium subscription
@dp.callback_query(F.data == "premium")
async def send_random_value(callback: types.CallbackQuery):
    global user_id
    global name
    global user2

    cursor.execute("SELECT * FROM users WHERE user = ?", (callback.from_user.id,))
    results = cursor.fetchone()

    print("user_id", callback.from_user.id)
    print("user2", user2)
    print(name)
    print(results)

    if results and (results[1] and datetime.strptime(str(results[1]), '%Y%m%d') >= datetime.now()):
        user_name = f"👱 Click to find out who wrote to you."
        mention = "[" + user_name + "](t.me/" + str(name) + ")"
        await callback.message.edit_text(mention, parse_mode="Markdown")
        await callback.message.answer(f"🎇 It was the user with id: {user2} and nickname: @{name}", parse_mode="Markdown")
    else:
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="💵 Buy",
            callback_data="buy")
        )

        await callback.message.answer(
            f"💁 To find out the sender, buy a 30-day subscription for just 169 rubles.",
            reply_markup=builder.as_markup()
        )
    await callback.answer()

# Main function to start the bot
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
