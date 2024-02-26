import re
import asyncio
import logging
from config_reader import config
from aiogram.types import Message
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.deep_linking import create_start_link, decode_payload

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

user_id = 0
canWrite = False


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

        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Анонимно ответить",
            callback_data=f"user_{str(message.from_user.id)}")
        )
        await bot.send_message(
            chat_id=user_id,
            text=f"💌 Вам отправили анонимное сообщение:\n\n{message.text}",
            reply_markup=builder.as_markup()
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

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
