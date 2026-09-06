# bo
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import init_db, get_or_create_user, update_user_language, get_products, get_product, update_balance, add_product
from languages import TEXTS

API_TOKEN = 'YOUR_BOT_TOKEN_HERE'
USDT_ADDRESS = 'TPxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
ADMIN_USERNAME = 'YourTelegramUsername'
ADMIN_ID = 123456789  # ضع آيدي تيليجرام الخاص بك هنا كأرقام

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class AddProduct(StatesGroup):
    name_ar = State()
    name_en = State()
    name_ru = State()
    price = State()
    details_ar = State()
    details_en = State()
    details_ru = State()

def get_main_menu(lang, user_id):
    t = TEXTS[lang]
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(t['menu_products'], callback_data="products_list"),
        InlineKeyboardButton(t['menu_account'], callback_data="my_account"),
        InlineKeyboardButton(t['menu_deposit'], callback_data="deposit"),
        InlineKeyboardButton(t['menu_lang'], callback_data="lang_menu"),
        InlineKeyboardButton(t['menu_support'], url=f"https://t.me/{ADMIN_USERNAME}")
    )
    if user_id == ADMIN_ID:
        kb.add(InlineKeyboardButton(t['admin_btn'], callback_data="admin_panel"))
    return kb

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    init_db()
    user_id = message.from_user.id
    user_data = get_or_create_user(user_id)
    lang = user_data['language']
    t = TEXTS[lang]
    await message.reply(t['welcome'], reply_markup=get_main_menu(lang, user_id))

@dp.callback_query_handler(lambda c: c.data == 'lang_menu')
async def lang_menu(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data = get_or_create_user(user_id)
    lang = user_data['language']
    t = TEXTS[lang]
    
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("العربية 🇸🇦", callback_data="setlang_ar"),
        InlineKeyboardButton("English 🇬🇧", callback_data="setlang_en"),
        InlineKeyboardButton("Русский 🇷🇺", callback_data="setlang_ru")
    )
    kb.add(InlineKeyboardButton(t['back'], callback_data="back_home"))
    await bot.edit_message_text("🌐 Select Language / اختر اللغة / Выберите язык:", callback_query.message.chat.id, callback_query.message.message_id, reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith('setlang_'))
async def set_language(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    new_lang = callback_query.data.split('_')[1]
    update_user_language(user_id, new_lang)
    t = TEXTS[new_lang]
    await callback_query.answer(t['lang_changed'], show_alert=True)
    await bot.edit_message_text(t['welcome'], callback_query.message.chat.id, callback_query.message.message_id, reply_markup=get_main_menu(new_lang, user_id))

@dp.callback_query_handler(lambda c: c.data == 'my_account')
async def show_account(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data = get_or_create_user(user_id)
    lang = user_data['language']
    t = TEXTS[lang]
    text = t['account_info'].format(user_id=user_id, password=user_data['password'], balance=user_data['balance'])
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton(t['back'], callback_data="back_home"))
    await bot.edit_message_text(text, callback_query.message.chat.id, callback_query.message.message_id, parse_mode="Markdown", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == 'deposit')
async def deposit_info(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data = get_or_create_user(user_id)
    lang = user_data['language']
    t = TEXTS[lang]
    text = t['deposit_info'].format(address=USDT_ADDRESS)
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton(t['back'], callback_data="back_home"))
    await bot.edit_message_text(text, callback_query.message.chat.id, callback_query.message.message_id, parse_mode="Markdown", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == 'admin_panel')
async def admin_panel(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id != ADMIN_ID:
        await callback_query.answer("غير مسموح لك!", show_alert=True)
        return
    user_data = get_or_create_user(user_id)
    lang = user_data['language']
    t = TEXTS[lang]
    
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(t['add_prod_btn'], callback_data="start_add_product"),
        InlineKeyboardButton("🔙 رجوع", callback_data="back_home")
    )
    await bot.edit_message_text(t['admin_panel_text'], callback_query.message.chat.id, callback_query.message.message_id, parse_mode="Markdown", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == 'start_add_product')
async def start_add_product(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        return
    user_data = get_or_create_user(callback_query.from_user.id)
    t = TEXTS[user_data['language']]
    
    await bot.send_message(callback_query.from_user.id, t['ask_name_ar'])
    await AddProduct.name_ar.set()
    await callback_query.answer()

@dp.message_handler(state=AddProduct.name_ar)
async def process_name_ar(message: types.Message, state: FSMContext):
    await state.update_data(name_ar=message.text)
    user_data = get_or_create_user(message.from_user.id)
    t = TEXTS[user_data['language']]
    await message.reply(t['ask_name_en'])
    await AddProduct.name_en.set()

@dp.message_handler(state=AddProduct.name_en)
async def process_name_en(message: types.Message, state: FSMContext):
    await state.update_data(name_en=message.text)
    user_data = get_or_create_user(message.from_user.id)
    t = TEXTS[user_data['language']]
    await message.reply(t['ask_name_ru'])
    await AddProduct.name_ru.set()

@dp.message_handler(state=AddProduct.name_ru)
async def process_name_ru(message: types.Message, state: FSMContext):
    await state.update_data(name_ru=message.text)
    user_data = get_or_create_user(message.from_user.id)
    t = TEXTS[user_data['language']]
    await message.reply(t['ask_price'])
    await AddProduct.price.set()

@dp.message_handler(state=AddProduct.price)
async def process_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        await message.reply("❌ السعر غير صحيح. يرجى إدخال رقم (مثال: 15.5):")
        return
    await state.update_data(price=price)
    user_data = get_or_create_user(message.from_user.id)
    t = TEXTS[user_data['language']]
    await message.reply(t['ask_details_ar'])
    await AddProduct.details_ar.set()

@dp.message_handler(state=AddProduct.details_ar)
async def process_details_ar(message: types.Message, state: FSMContext):
    await state.update_data(details_ar=message.text)
    user_data = get_or_create_user(message.from_user.id)
    t = TEXTS[user_data['language']]
    await message.reply(t['ask_details_en'])
    await AddProduct.details_en.set()

@dp.message_handler(state=AddProduct.details_en)
async def process_details_en(message: types.Message, state: FSMContext):
    await state.update_data(details_en=message.text)
    user_data = get_or_create_user(message.from_user.id)
    t = TEXTS[user_data['language']]
    await message.reply(t['ask_details_ru'])
    await AddProduct.details_ru.set()

@dp.message_handler(state=AddProduct.details_ru)
async def process_details_ru(message: types.Message, state: FSMContext):
    data = await state.get_data()
    add_product(
        data['name_ar'], data['name_en'], data['name_ru'],
        data['price'],
        data['details_ar'], data['details_en'], data['details_ru']
    )
    await state.finish()
    user_data = get_or_create_user(message.from_user.id)
    t = TEXTS[user_data['language']]
    await message.reply(t['product_added_success'], reply_markup=get_main_menu(user_data['language'], message.from_user.id))

@dp.message_handler(commands=['addbalance'])
async def cmd_add_balance(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) != 3:
        await message.reply("الصيغة الصحيحة:\n`/addbalance user_id amount`", parse_mode="Markdown")
        return
    try:
        target_user_id = int(args[1])
        amount = float(args[2])
        get_or_create_user(target_user_id)
        update_balance(target_user_id, amount)
        await message.reply(f"✅ تم إضافة {amount} USDT بنجاح للمستخدم `{target_user_id}`", parse_mode="Markdown")
    except ValueError:
        await message.reply("❌ تأكد من أن الآيدي والمبلغ أرقام صحيحة.")

@dp.callback_query_handler(lambda c: c.data == 'products_list')
async def show_products(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data = get_or_create_user(user_id)
    lang = user_data['language']
    t = TEXTS[lang]
    
    products = get_products()
    kb = InlineKeyboardMarkup(row_width=1)
    for prod in products:
        prod_id, n_ar, n_en, n_ru, price = prod
        name = n_ar if lang == 'ar' else (n_en if lang == 'en' else n_ru)
        kb.add(InlineKeyboardButton(f"{name} - {price}$", callback_data=f"prod_{prod_id}"))
    kb.add(InlineKeyboardButton(t['back'], callback_data="back_home"))
    await bot.edit_message_text(t['choose_product'], callback_query.message.chat.id, callback_query.message.message_id, reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith('prod_'))
async def product_details(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data = get_or_create_user(user_id)
    lang = user_data['language']
    t = TEXTS[lang]
    
    prod_id = int(callback_query.data.split('_')[1])
    product = get_product(prod_id)
    if not product:
        await callback_query.answer("Product not found!", show_alert=True)
        return
        
    n_ar, n_en, n_ru, price, d_ar, d_en, d_ru = product
    name = n_ar if lang == 'ar' else (n_en if lang == 'en' else n_ru)
    text = f"📦 **{name}**\n💵 Price: **{price} USDT**"
    
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(t['buy_btn'], callback_data=f"buy_{prod_id}"),
        InlineKeyboardButton(t['back'], callback_data="products_list")
    )
    await bot.edit_message_text(text, callback_query.message.chat.id, callback_query.message.message_id, parse_mode="Markdown", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith('buy_'))
async def buy_product(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    prod_id = int(callback_query.data.split('_')[1])
    user_data = get_or_create_user(user_id)
    lang = user_data['language']
    t = TEXTS[lang]
    
    product = get_product(prod_id)
    n_ar, n_en, n_ru, price, d_ar, d_en, d_ru = product
    name = n_ar if lang == 'ar' else (n_en if lang == 'en' else n_ru)
    details = d_ar if lang == 'ar' else (d_en if lang == 'en' else d_ru)
    
    if user_data['balance'] < price:
        await callback_query.answer(t['insufficient_balance'], show_alert=True)
        return
        
    update_balance(user_id, -price)
    new_balance = user_data['balance'] - price
    success_text = t['purchase_success'].format(name=name, price=price, balance=new_balance, details=details)
    
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton(t['back'], callback_data="back_home"))
    await bot.edit_message_text(success_text, callback_query.message.chat.id, callback_query.message.message_id, parse_mode="Markdown", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == 'back_home')
async def back_home(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data = get_or_create_user(user_id)
    lang = user_data['language']
    t = TEXTS[lang]
    await bot.edit_message_text(t['welcome'], callback_query.message.chat.id, callback_query.message.message_id, reply_markup=get_main_menu(lang, user_id))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
  
