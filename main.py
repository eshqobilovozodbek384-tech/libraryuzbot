import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import google.generativeai as genai


TOKEN = "8962611658:AAErildiEbbB6TstoxWWC-9xuDWNiaShDUw"
GOOGLE_API_KEY = "AQ.Ab8RN6K1sva7gHy08W20xhOhj9GV7cAKgZkuhgki_9i2vEe5LA"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

user_sessions = {}

# =====================
# YORDAMCHI FUNKSIYALAR
# =====================

def split_text(text, max_length=4000):
    return [
        text[i:i + max_length]
        for i in range(0, len(text), max_length)
    ]


def get_genre_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📚 Sarguzasht",
                    callback_data="genre_sarguzasht"
                ),
                InlineKeyboardButton(
                    text="💡 Ilm-fan",
                    callback_data="genre_ilm"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎭 Roman",
                    callback_data="genre_roman"
                ),
                InlineKeyboardButton(
                    text="✨ Motivatsiya",
                    callback_data="genre_motivatsiya"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🕰 Tarixiy",
                    callback_data="genre_tarixiy"
                ),
                InlineKeyboardButton(
                    text="🔍 Detektiv",
                    callback_data="genre_detektiv"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🐉 Fantastika",
                    callback_data="genre_fantastika"
                ),
                InlineKeyboardButton(
                    text="💼 Biznes",
                    callback_data="genre_biznes"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🧠 Psixologiya",
                    callback_data="genre_psixologiya"
                ),
                InlineKeyboardButton(
                    text="👶 Bolalar",
                    callback_data="genre_bolalar"
                )
            ]
        ]
    )


async def get_ai_response(user_id: int, user_text: str):
    try:
        if user_id not in user_sessions:
            user_sessions[user_id] = model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [
                            "Sen kitoblar bo'yicha professional maslahatchisan. "
                            "Faqat o'zbek tilida javob ber. "
                            "Kitob tavsiyalarini chiroyli formatda yoz."
                        ]
                    }
                ]
            )

        chat = user_sessions[user_id]

        response = await asyncio.to_thread(
            chat.send_message,
            user_text
        )

        return response.text

    except Exception as e:
        logging.error(f"AI xatosi: {e}")
        return (
            "❌ AI javobini olishda xatolik yuz berdi.\n\n"
            f"Xato: {e}"
        )


async def send_long_message(
    chat_id: int,
    message_id: int,
    text: str
):
    parts = split_text(text)

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=parts[0]
    )

    for part in parts[1:]:
        await bot.send_message(chat_id, part)


# =====================
# START
# =====================

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "📚 Assalomu alaykum!\n\n"
        "Men AI kitob maslahatchisiman.\n"
        "Janr tanlang yoki savolingizni yozing.",
        reply_markup=get_genre_keyboard()
    )


# =====================
# JANR TUGMALARI
# =====================

@dp.callback_query(F.data.startswith("genre_"))
async def callback_handler(callback: types.CallbackQuery):

    await callback.answer()

    genre = callback.data.replace("genre_", "")

    msg = await callback.message.answer(
        "🔍 Kitoblar qidirilmoqda..."
    )

    prompt = (
        f"{genre} janrida 5 ta eng yaxshi kitob tavsiya qil. "
        f"Har biri uchun:\n"
        f"- Muallif\n"
        f"- Qisqacha tavsif\n"
        f"- Nima uchun o‘qish kerakligi"
    )

    ai_answer = await get_ai_response(
        callback.from_user.id,
        prompt
    )

    await send_long_message(
        callback.message.chat.id,
        msg.message_id,
        ai_answer
    )


# =====================
# ODATIY XABARLAR
# =====================

@dp.message()
async def text_handler(message: types.Message):

    msg = await message.answer(
        "🤖 O'ylayapman..."
    )

    ai_answer = await get_ai_response(
        message.from_user.id,
        message.text
    )

    await send_long_message(
        message.chat.id,
        msg.message_id,
        ai_answer
    )


# =====================
# ISHGA TUSHIRISH
# =====================

async def main():
    print("✅ Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⛔ Bot to'xtatildi.")