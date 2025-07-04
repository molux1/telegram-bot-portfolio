import telebot
import json
import os
from telebot import types

API_TOKEN = '7180822092:AAF60_2g4YTd87n1UTkYC-DBOYkxTRkzW4I'
ADMIN_ID = 2072383039

bot = telebot.TeleBot(API_TOKEN)
PORTFOLIO_FILE = 'portfolio.json'

# Создание файла, если его нет
if not os.path.exists(PORTFOLIO_FILE):
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump([], f)

def load_portfolio():
    with open(PORTFOLIO_FILE, 'r') as f:
        return json.load(f)

def save_portfolio(data):
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(data, f)

languages = ['ru', 'en', 'pl']
user_lang = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru'),
        types.InlineKeyboardButton("🇬🇧 English", callback_data='lang_en'),
        types.InlineKeyboardButton("🇵🇱 Polski", callback_data='lang_pl')
    )
    bot.send_message(message.chat.id, "👋 Welcome to Molux AI Portfolio!\n\n🌍 Please choose your language:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_language(call):
    lang = call.data.split('_')[1]
    user_lang[call.from_user.id] = lang
    texts = {
        'ru': "📸 Посмотрите мои работы или добавьте свои!",
        'en': "📸 Check out my work or add your own!",
        'pl': "📸 Zobacz moje prace lub dodaj swoje!"
    }
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🖼 Портфолио / Portfolio", callback_data='view_portfolio'))
    markup.add(types.InlineKeyboardButton("📬 Связаться", url="https://t.me/molux52"))
    markup.add(types.InlineKeyboardButton("📺 YouTube", url="https://www.youtube.com/@molux52"))
    markup.add(types.InlineKeyboardButton("💻 GitHub", url="https://github.com/molux1"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=texts[lang], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'view_portfolio')
def view_portfolio(call):
    data = load_portfolio()
    if not data:
        bot.send_message(call.message.chat.id, "😢 Портфолио пока пусто.")
        return
    for item in data:
        bot.send_photo(call.message.chat.id, item['file_id'], caption=item['caption'])

@bot.message_handler(commands=['add'])
def prompt_add(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "📎 Отправь фото с подписью — оно будет добавлено в портфолио.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.from_user.id == ADMIN_ID:
        if not message.caption:
            bot.reply_to(message, "⚠️ Добавь подпись к фото!")
            return
        file_id = message.photo[-1].file_id
        caption = message.caption
        data = load_portfolio()
        data.append({'file_id': file_id, 'caption': caption})
        save_portfolio(data)
        bot.reply_to(message, "✅ Добавлено!")

@bot.message_handler(commands=['remove'])
def remove_last(message):
    if message.from_user.id == ADMIN_ID:
        data = load_portfolio()
        if not data:
            bot.send_message(message.chat.id, "❌ Портфолио пусто.")
            return
        removed = data.pop()
        save_portfolio(data)
        bot.send_message(message.chat.id, f"🗑 Удалено: {removed['caption']}")

print("🤖 Bot is running...")
bot.polling(none_stop=True)