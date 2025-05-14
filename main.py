import json
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.enums import ParseMode

# Токен Telegram-бота
TOKEN = "8081332992:AAFyARu3WQjkvlXQU9PBKUNR3Sb1U7yl2Mk"

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Загрузка офферов из JSON
try:
    with open("offers.json", "r", encoding="utf-8") as f:
        offers = json.load(f)
except FileNotFoundError:
    print("Файл offers.json не найден!")
    exit(1)

def build_offer_keyboard(offer_list):
    keyboard = []
    for offer in offer_list:
        keyboard.append([InlineKeyboardButton(text=offer['title'], url=offer['link'])])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.message(Command("start"))
async def cmd_start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Микрозаймы", callback_data="loans")],
        [InlineKeyboardButton(text="Дебетовые карты", callback_data="cards")]
    ])
    await message.answer("Привет! Я Ашак Бот. Выбери, что тебя интересует:", reply_markup=kb)

@dp.callback_query()
async def show_offers(callback_query):
    category = callback_query.data
    if category in offers:
        keyboard = build_offer_keyboard(offers[category])
        text = f"Вот актуальные предложения по категории *{ 'Займы' if category == 'loans' else 'Карты' }*:"
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
    else:
        await callback_query.answer("Неизвестная категория")

# === Удаление вебхука перед запуском ===
async def main():
    await bot.delete_webhook(drop_pending_updates=True)  # 👈 Удаляем вебхук
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
