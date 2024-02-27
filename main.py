import re
import asyncio
import logging

from aiogram.enums import ContentType

from config_reader import config, PAYMENTS_TOKEN
from aiogram.types import Message, PreCheckoutQuery, successful_payment, inline_keyboard_markup
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.deep_linking import create_start_link, decode_payload

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

PRICE = types.LabeledPrice(label="Подписка на 1 месяц", amount=169 * 100)  # в копейках (руб)
user_id = 0
canWrite = False


@dp.message(Command("buy"))
async def buy(message: types.Message):
    if PAYMENTS_TOKEN.split(':')[1] == 'TEST':
        await bot.send_message(message.chat.id, "Тестовый платеж!!!")

    await bot.send_invoice(message.chat.id,
                           title="Подписка на бота",
                           description="Активация подписки на бота на 1 месяц",
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

    await bot.send_message(message.chat.id,
                           f"Платеж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!!!")


@dp.message(CommandStart(deep_link=True, magic=F.args.regexp(re.compile(r'user_(\d+)'))))
async def cmd_start_book(message: Message, command: CommandObject):
    global user_id
    global canWrite

    user_id = command.args.split("_")[1]
    await message.answer(f"Напишите сообщение {user_id}:")
    canWrite = True


@dp.message(CommandStart())
async def process_start_command(message: types.Message):
    link = f"t.me/stavrmoris_testbot?start=user_{str(message.from_user.id)}"
    keyboard = InlineKeyboardBuilder()

    share_button = types.InlineKeyboardButton(
        text="Поделиться",
        switch_inline_query=f"\n💌 Напишите мне анонимную валентинку:\n\n{link}"
    )

    keyboard.add(share_button)

    await message.answer(
        f"❤️ Твоя ссылка для признаний:\n{link}\n\nЗакрепи эту ссылку в профиле или поделись с друзьями, чтобы получать анонимные валентинки!",
        reply_markup=keyboard.as_markup()
    )


@dp.message(F.text)
async def any_message(message: Message):
    global canWrite

    if canWrite:
        await message.answer("Ваше сообщение успешно отправлено!")
        buttons = [
            [types.InlineKeyboardButton(
                text="Анонимно ответить",
                callback_data=f"user_{str(message.from_user.id)}"
            )],
            [types.InlineKeyboardButton(
                text="Узнать отправителя",
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


@dp.callback_query(F.data.startswith("user_"))
async def callbacks_num(callback: types.CallbackQuery):
    global user_id
    global canWrite

    user_id = callback.data.split("_")[1]
    canWrite = True
    await callback.message.answer(f"Напишите сообщение {user_id}:")
    await callback.answer()

@dp.callback_query(F.data == "premium")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer(str("Для того чтобы узнать отправителя, необходимо оформить премиум"))

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
