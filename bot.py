import asyncio
import logging
import os
import tempfile
from pathlib import Path
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from converter import convert
from document_converter import translate_document

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
MODES = [('latin','new','Lotin → Yangi'),('cyr','new','Kirill → Yangi'),
         ('new','cyr','Yangi → Kirill'),('new','latin','Yangi → Lotin'),
         ('latin','cyr','Lotin → Kirill'),('cyr','latin','Kirill → Lotin')]
choices = {}
dp = Dispatcher()
SUPPORTED_DOCUMENTS = {'.docx', '.xlsx'}
MAX_DOCUMENT_SIZE = 20 * 1024 * 1024

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
    await call.message.answer(f'✅ {MODES[idx][2]}\nОтправьте текст, Word (.docx) или Excel (.xlsx). Для смены направления: /start')

@dp.message(F.document)
async def translate_file(message: Message):
    idx = choices.get(message.from_user.id)
    if idx is None:
        await message.answer('Сначала выберите направление:', reply_markup=keyboard()); return

    document = message.document
    filename = Path(document.file_name or '').name
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_DOCUMENTS:
        await message.answer('Поддерживаются только Word (.docx) и Excel (.xlsx).'); return
    if document.file_size and document.file_size > MAX_DOCUMENT_SIZE:
        await message.answer('Файл больше 20 МБ. Отправьте файл меньшего размера.'); return

    source, target, _ = MODES[idx]
    await message.answer('Перевожу документ...')
    try:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / f'input{extension}'
            output_path = Path(directory) / f'translated{extension}'
            await message.bot.download(document, destination=input_path)
            await asyncio.to_thread(translate_document, input_path, output_path, source, target)
            output_name = f'{Path(filename).stem}_translated{extension}'
            await message.answer_document(FSInputFile(output_path, filename=output_name), caption='Готово.')
    except Exception:
        logging.exception('Document translation failed')
        await message.answer('Не удалось обработать файл. Проверьте, что он не повреждён, и попробуйте ещё раз.')

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
