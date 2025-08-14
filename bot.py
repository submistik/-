# bot.py
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import executor
import random
import os

# === НАСТРОЙКИ ===
API_TOKEN = "YOUR_BOT_TOKEN"  # Замените на токен вашего бота
CHANNEL_ID = "@your_channel"  # Замените на ваш канал
CHANNEL_URL = "https://t.me/your_channel"

# === ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ===
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# База логотипов: "Название" -> "путь к изображению"
logos = {}
for file in os.listdir("logos"):
    if file.endswith((".png", ".jpg", ".jpeg")):
        name = os.path.splitext(file)[0].capitalize()
        logos[name] = f"logos/{file}"

user_data = {}  # user_id: {score, current_answer}

# === КОМАНДЫ ===
@dp.message_handler(commands=['start'])
async def start(message: Message):
    user_id = message.from_user.id
    user_data[user_id] = {"score": 0, "current_answer": None}

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🎮 Играть", callback_data="play"))
    kb.add(InlineKeyboardButton("📊 Счёт", callback_data="score"))
    kb.add(InlineKeyboardButton("📢 Подписаться", url=CHANNEL_URL))

    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n"
        "Добро пожаловать в игру *«Угадай логотип»*!\n\n"
        "🎯 Угадывай логотипы и получай очки!\n"
        "🎁 Топ-игроки получат шанс на VIP-рекламу в канале!",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.callback_query_handler(lambda c: c.data == "play")
async def play(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    logo_name = random.choice(list(logos.keys()))
    user_data[user_id]["current_answer"] = logo_name

    with open(logos[logo_name], 'rb') as photo:
        await bot.send_photo(
            chat_id=callback_query.message.chat.id,
            photo=photo,
            caption="🔍 Угадайте логотип! Напишите название:"
        )
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "score")
async def show_score(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    score = user_data.get(user_id, {}).get("score", 0)
    await callback_query.message.answer(f"📊 Ваш счёт: {score} очков")
    await callback_query.answer()

# Проверка ответа
@dp.message_handler()
async def check_answer(message: Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.answer("Начните с /start")
        return

    current_answer = user_data[user_id]["current_answer"]
    if not current_answer:
        return

    if message.text.strip().lower() == current_answer.lower():
        user_data[user_id]["score"] += 1
        user_data[user_id]["current_answer"] = None

        await message.answer("✅ Правильно! +1 очко! 🎉")
        
        # Кнопки после правильного ответа
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("🎮 Следующий", callback_data="play"))
        kb.add(InlineKeyboardButton("🏆 Топ", callback_data="score"))
        
        await message.answer("Продолжим?", reply_markup=kb)
    else:
        await message.answer("❌ Неверно. Попробуй ещё раз или начни заново.")

# === ЗАПУСК ===
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
