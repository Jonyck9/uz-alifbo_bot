import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from converter import convert

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
MODES = [('latin','new','Lotin → Yangi'),('cyr','new','Kirill → Yangi'),
         ('new','cyr','Yangi → Kirill'),('new','latin','Yangi → Lotin'),
         ('latin','cyr','Lotin → Kirill'),('cyr','latin','Kirill → Lotin')]
choices = {}
dp = Dispatcher()

def keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=MODES[i][2],callback_data=f'mode:{i}'),
         InlineKeyboardButton(text=MODES[i+1][2],callback_data=f'mode:{i+1}')]
        for i in range(0,6,2)])

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer('Assalomu alaykum! 🇺🇿\nВыберите направление перевода:',reply_markup=keyboard())

@dp.callback_query(F.data.startswith('mode:'))
async def choose(call: CallbackQuery):
    idx=int(call.data.split(':')[1])
    if idx not in range(len(MODES)):
        await call.answer('Неверный режим'); return
    choices[call.from_user.id]=idx
    await call.answer('Направление выбрано')
    await call.message.answer(f'✅ {MODES[idx][2]}\nОтправьте текст. Для смены направления: /start')

@dp.message(F.text)
async def translate(message: Message):
    idx=choices.get(message.from_user.id)
    if idx is None:
        await message.answer('Сначала выберите направление:',reply_markup=keyboard());return
    source,target,_=MODES[idx]
    result=convert(message.text,source,target)
    if len(result)>4000:
        await message.answer('Текст слишком длинный. Отправьте его частями.');return
    await message.answer(result)

def get_bot():
    if not TOKEN or TOKEN == 'PASTE_YOUR_BOTFATHER_TOKEN_HERE':
        raise RuntimeError('Добавьте BOT_TOKEN в переменные окружения')
    return Bot(TOKEN)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(get_bot())

if __name__=='__main__':
    asyncio.run(main())
