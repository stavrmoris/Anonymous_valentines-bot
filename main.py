import re
import asyncio
import logging
import sqlite3

from datetime import datetime
from aiogram.enums import ContentType
from config_reader import config, PAYMENTS_TOKEN
from aiogram.types import Message
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

connection = sqlite3.connect('data.db')
cursor = connection.cursor()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

PRICE = types.LabeledPrice(label="Подписка на 1 месяц", amount=169 * 100)  # в копейках (руб)
user_id = 0
canWrite = False


def date_integer(dt_time):
    return 10000 * dt_time.year + 100 * dt_time.month + dt_time.day


@dp.callback_query(F.data == "buy")
async def buy(message: types.Message):
    if PAYMENTS_TOKEN.split(':')[1] == 'TEST':
        await message.answer("Тестовый платеж!!!")

    await bot.send_invoice(message.from_user.id,
                           title="Подписка на бота",
                           description="🤖 Активация подписки на бота на 30 дней",
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


@dp.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} = {v}")

    cursor.execute('INSERT INTO Users (user, date) VALUES (?, ?)',
                   (f'{message.from_user.id}', date_integer(datetime.datetime.now() + datetime.timedelta(days=30))))
    connection.commit()
    connection.close()

    await bot.send_message(message.chat.id,
                           f"💵 Платеж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!!!")


@dp.message(CommandStart(deep_link=True, magic=F.args.regexp(re.compile(r'user_(\d+)'))))
async def cmd_start_book(message: Message, command: CommandObject):
    global user_id
    global canWrite

    user_id = command.args.split("_")[1]
    await message.answer(f"✉️ Напишите сообщение:")
    canWrite = True


@dp.message(CommandStart())
async def process_start_command(message: types.Message):
    message_buttons = [
        [
            types.InlineKeyboardButton(
                text="Отправить сообщение по ссылке",
                callback_data="message_link"
            )
        ],
        [
            types.InlineKeyboardButton(
                text="Отправить сообщение, используя сообщение пользователя",
                callback_data="message_username"
            )
        ]
    ]

    message_builder = types.InlineKeyboardMarkup(inline_keyboard=message_buttons)

    await message.answer(
        "❤️ Твоя ссылка для признаний:{link}Закрепи эту ссылку в профиле или поделись с друзьями, чтобы получать анонимные валентинки!",
        reply_markup=message_builder
    )
    # link = f"t.me/stavrmoris_testbot?start=user_{str(message.from_user.id)}"
    # keyboard = InlineKeyboardBuilder()
    #
    # share_button = types.InlineKeyboardButton(
    #     text="🔗 Поделиться",
    #     switch_inline_query=f"\n💌 Напишите мне анонимную валентинку:\n\n{link}"
    # )
    #
    # keyboard.add(share_button)
    #
    # await message.answer(
    #     f"❤️ Твоя ссылка для признаний:\n{link}\n\nЗакрепи эту ссылку в профиле или поделись с друзьями, чтобы получать анонимные валентинки!",
    #     reply_markup=keyboard.as_markup()
    # )


@dp.message(F.text)
async def any_message(message: Message):
    global canWrite

    if canWrite:
        await message.answer("Ваше сообщение успешно отправлено!")
        buttons = [
            [types.InlineKeyboardButton(
                text="🥸 Анонимно ответить",
                callback_data=f"user_{str(message.from_user.id)}"
            )],
            [types.InlineKeyboardButton(
                text="🥷 Узнать отправителя",
                callback_data="premium"
            )]
        ]
        builder = types.InlineKeyboardMarkup(inline_keyboard=buttons)

        await bot.send_message(
            chat_id=user_id,
            text=f"💌 Вам отправили анонимное сообщение:\n\n{message.text}",
            reply_markup=builder
        )

        canWrite = False
@dp.message(F.text)
def link(value: str, message: types.Message):
    value = f"t.me/stavrmoris_testbot?start=user_{str(message.from_user.id)}"
    return value
@dp.callback_query(F.data.startswith("message_link"))
async def message_link(callback: types.CallbackQuery):
    value = link
    keyboard = InlineKeyboardBuilder()

    share_button = types.InlineKeyboardButton(
        text="🔗 Поделиться",
        switch_inline_query=f"\n💌 Напишите мне анонимную валентинку:\n\n{value}"
    )

    keyboard.add(share_button)

    await callback.message.answer(

        text=f"❤️ Твоя ссылка для признаний:\n{value}\n\nЗакрепи эту ссылку в профиле или поделись с друзьями, чтобы получать анонимные валентинки!",
        reply_markup=keyboard.as_markup(),
    )
@dp.callback_query(F.data.startswith("user_"))
async def callbacks_num(callback: types.CallbackQuery):
    global user_id
    global canWrite

    user_id = callback.data.split("_")[1]
    canWrite = True
    await callback.message.answer(f"✉️ Напишите сообщение {user_id}:")
    await callback.answer()


@dp.callback_query(F.data == "premium")
async def send_random_value(callback: types.CallbackQuery):
    global user_id
    cursor.execute("SELECT * FROM users WHERE user = ?", (user_id,))
    results = cursor.fetchone()

    print(user_id)
    print(results)
    print(results[1])

    if (results and user_id in results) and (results[1] and datetime.strptime(str(results[1]), '%Y%m%d') >= datetime.now()):
        user_name = "👱 Вам написал этот пользователь."
        mention = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
        await bot.send_message(callback.from_user.id, mention, parse_mode="Markdown")
    else:
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="💵 Купить",
            callback_data="buy")
        )

        await callback.message.answer(
            f"💁 Чтобы узнать отправителя - купите 30 дневную подписку на бота всего за 169 руб.",
            reply_markup=builder.as_markup()
        )
    await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
