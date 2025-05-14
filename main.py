import json
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.enums import ParseMode

TOKEN = "8081332992:AAFyARu3WQjkvlXQU9PBKUNR3Sb1U7yl2Mk"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Загрузка офферов
with open("offers.json", "r", encoding="utf-8") as f:
    offers = json.load(f)

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

@dp.callback_query(F.data.in_(["loans", "cards"]))
async def show_offers(callback_query):
    category = callback_query.data
    keyboard = build_offer_keyboard(offers[category])
    await callback_query.message.edit_text(
        f"Вот актуальные предложения по категории *{ 'Займы' if category == 'loans' else 'Карты' }*:",
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))