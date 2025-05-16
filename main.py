import os
import json
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.enums import ParseMode
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # Укажите ADMIN_ID в Railway или .env

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Файл для хранения пользователей
USERS_DB = "users.json"

# Загрузка офферов
try:
    with open("offers.json", "r", encoding="utf-8") as f:
        offers = json.load(f)
except FileNotFoundError:
    print("Файл offers.json не найден!")
    exit(1)

# --- Работа с пользователями ---
def load_users():
    if os.path.exists(USERS_DB):
        with open(USERS_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(data):
    with open(USERS_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --- Клавиатуры ---
def build_offer_keyboard(offer_list):
    keyboard = []
    for offer in offer_list:
        keyboard.append([InlineKeyboardButton(text=offer['title'], url=offer['link'])])
    keyboard.append([InlineKeyboardButton(text="⬅ Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Главное меню
main_menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💳 Дебетовые карты", callback_data="cards")],
    [InlineKeyboardButton(text="🔖 Платежные стикеры", callback_data="stickers")],
    [InlineKeyboardButton(text="🧾 Вклады", callback_data="deposits")],
    [InlineKeyboardButton(text="💸 Займы", callback_data="loans")],
    [InlineKeyboardButton(text="🚗 Автокредиты", callback_data="auto_loans")],
    [InlineKeyboardButton(text="💰 Кредиты наличными", callback_data="cash_loans")],
    [InlineKeyboardButton(text="💼 Работа в банках", callback_data="bank_jobs")]
])

# --- Команды ---
@dp.message(Command("start"))
@dp.message(Command("menu"))
async def cmd_start(message: Message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id not in users:
        users[user_id] = {
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_seen": message.date.isoformat()
        }
        save_users(users)

    await message.answer("Привет! Я Ашак Бот. Выбери, что тебя интересует:", reply_markup=main_menu_kb)

@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к админке.")
        return

    users = load_users()
    total = len(users)
    last_5 = "\n".join([
        f"{uid} — @{data.get('username', 'нет')}, {data.get('first_name')}"
        for uid, data in list(users.items())[:5]
    ])

    stats = f"🔐 Статистика бота:\n\n👥 Всего пользователей: {total}\n\n последние 5:\n{last_5 or 'Нет данных'}"
    await message.answer(stats)

# --- Callback ---
@dp.callback_query()
async def handle_callback(callback: CallbackQuery):
    category = callback.data

    if category == "back":
        await callback.message.edit_text("Выбери, что тебя интересует:", reply_markup=main_menu_kb)
        return

    if category in offers:
        keyboard = build_offer_keyboard(offers[category])
        title_map = {
            "cards": "💳 Дебетовые карты",
            "stickers": "🔖 Платежные стикеры",
            "deposits": "🧾 Вклады",
            "loans": "💸 Займы",
            "auto_loans": "🚗 Автокредиты",
            "cash_loans": "💰 Кредиты наличными",
            "bank_jobs": "💼 Работа в банках"
        }
        text = f"Вот актуальные предложения по категории *{title_map.get(category, category)}*:"
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
    else:
        await callback.answer("Неизвестная категория")

# === Запуск бота ===
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
