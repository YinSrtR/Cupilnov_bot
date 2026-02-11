import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from fuzzywuzzy import fuzz
import os

# ============================================
# ТВОИ ДАННЫЕ
# ============================================
TOKEN = "8010806544:AAHCyeADuAyv3TPRCxFISxQNHm6c0IHMWj0"
ADMIN_ID = 5329758526
AUTHOR_CONTACT = "@The_Yin"
# ============================================

VIDEO_DATABASE = {
    "the last of us": {
        "display_name": "The Last of Us",
        "series": {
            "1": "placeholder",
            "2": "placeholder",
            "3": "placeholder",
        }
    },
    "resident evil": {
        "display_name": "Resident Evil 2",
        "series": {
            "1": "placeholder",
            "2": "placeholder",
        }
    },
    "silent hill": {
        "display_name": "Silent Hill",
        "series": {
            "1": "placeholder",
        }
    },
    "trip": {
        "display_name": "TRIP",
        "series": {
            "1": "placeholder",
            "2": "placeholder",
        }
    }
}

logging.basicConfig(level=logging.INFO)

def is_admin(user_id):
    return user_id == ADMIN_ID

def find_best_match(query, database, threshold=60):
    query = query.lower().strip()
    if query in database:
        return query
    best_match = None
    best_ratio = 0
    for game_key in database.keys():
        ratio = fuzz.token_sort_ratio(query, game_key)
        if ratio > best_ratio and ratio >= threshold:
            best_ratio = ratio
            best_match = game_key
    return best_match

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = f"""
🎮 **ВИДЕО КУПЛИНОВА**

Автор: @kupilnov_official

📝 Напиши название игры:
• The Last of Us
• Resident Evil
• Silent Hill
• TRIP

✅ Понимаю опечатки
❓ Нет видео? Пиши {AUTHOR_CONTACT}
"""
    await update.message.reply_text(welcome, parse_mode='Markdown')

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ Доступ запрещен.")
        return
    await update.message.reply_text("🛠 Админ-панель\n\nОтправь видео — получишь file_id")

async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.video:
        file_id = update.message.video.file_id
        await update.message.reply_text(f"✅ file_id:\n`{file_id}`", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Отправь видео!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.startswith('/'):
        return
    query = update.message.text
    game_key = find_best_match(query, VIDEO_DATABASE)
    if not game_key:
        await update.message.reply_text(f"❌ Не найдено. Пиши {AUTHOR_CONTACT}")
        return
    game_data = VIDEO_DATABASE[game_key]
    series_list = sorted(game_data['series'].keys(), key=lambda x: int(x) if x.isdigit() else 0)
    keyboard = []
    for i in range(0, len(series_list), 4):
        row = []
        for s in series_list[i:i+4]:
            row.append(InlineKeyboardButton(f"🎬 Серия {s}", callback_data=f"{game_key}|{s}"))
        keyboard.append(row)
    await update.message.reply_text(
        f"🎮 {game_data['display_name']}\n📼 {len(series_list)} серий",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    game_key, series_num = query.data.split('|')
    file_id = VIDEO_DATABASE[game_key]['series'][series_num]
    if file_id and file_id != "placeholder":
        await query.message.reply_video(video=file_id, caption=f"{VIDEO_DATABASE[game_key]['display_name']} - Серия {series_num}")
    else:
        await query.message.reply_text("⏳ Видео скоро появится!")

def main():
    print("🚀 Запуск бота...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(MessageHandler(filters.VIDEO, get_file_id))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    print("✅ Бот работает!")
    app.run_polling()

if __name__ == '__main__':
    main()
