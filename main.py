import os
import json
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.enums import ParseMode
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # Укажите ADMIN_ID в переменных среды

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Загрузка офферов
try:
    with open("offers.json", "r", encoding="utf-8") as f:
        offers = json.load(f)
except FileNotFoundError:
    print("Файл offers.json не найден!")
    exit(1)

# Функция для создания клавиатуры из списка офферов
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

# Команда /start и /menu
@dp.message(Command("start"))
@dp.message(Command("menu"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я Ашак Бот. Выбери, что тебя интересует:", reply_markup=main_menu_kb)

# Админка — только для одного пользователя
@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к админке.")
        return

    await message.answer("🔐 Вы вошли в админку.\nДоступные команды:\n• /menu — главное меню")

# Обработчик всех callback'ов
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

# === Удаление вебхука перед запуском ===
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
