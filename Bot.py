import logging
import uuid
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import firebase_admin
from firebase_admin import credentials, db

# ---------------- Firebase инициализация ----------------
cred = credentials.Certificate('firebase-key.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://hot-wheels-1-default-rtdb.europe-west1.firebasedatabase.app/"# укажи URL своей базы
})

# Ссылка на корень БД
root_ref = db.reference('/activation_codes')

# ---------------- Логирование ----------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(name)

# ---------------- Команды бота ----------------

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Привет! Выберите подписку:\n"
        "1. Подписка на месяц — 149₽\n"
        "2. Подписка на год — 1099₽\n\n"
        "Отправьте 1 или 2, чтобы получить ссылку на оплату."
    )

def choose_plan(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    text = update.message.text.strip()

    if text == '1':
        pay_link = "https://t.me/UnionBot?start=pay_month"  # Заменить на реальную ссылку тарифа
        update.message.reply_text(f"Оплатите подписку на месяц по ссылке:\n{pay_link}")
    elif text == '2':
        pay_link = "https://t.me/UnionBot?start=pay_year"  # Заменить на реальную ссылку тарифа
        update.message.reply_text(f"Оплатите подписку на год по ссылке:\n{pay_link}")
    else:
        update.message.reply_text("Пожалуйста, отправьте '1' или '2'.")

# Эмуляция получения уведомления об оплате (для теста)
def confirm_payment(update: Update, context: CallbackContext):
    # Команда для теста: /confirm
    user_id = str(update.message.from_user.id)
    args = context.args
    if not args:
        update.message.reply_text("Использование: /confirm <month|year>")
        return
    plan = args[0].lower()
    if plan not in ['month', 'year']:
        update.message.reply_text("План должен быть 'month' или 'year'")
        return

    # Генерируем код
    code = str(uuid.uuid4()).replace("-", "").upper()[:10]

    # Сохраняем в Firebase
    root_ref.child(user_id).set({
        'code': code,
        'plan': plan,
        # Можно добавить дату активации, срок действия и т.п.
    })

    update.message.reply_text(f"Оплата подтверждена. Ваш код активации: {code}")

def get_code(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    data = root_ref.child(user_id).get()
    if data and 'code' in data:
        update.message.reply_text(f"Ваш код активации: {data['code']}\nПодписка: {data.get('plan', 'не указана')}")
    else:
        update.message.reply_text("Код активации не найден. Пожалуйста, оплатите подписку.")

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "/start — начать\n"
        "/confirm <month|year> — подтвердить оплату (тест)\n"
        "/code — получить код активации\n"
        "/help — помощь"
    )

def main():
    # Вставь сюда токен своего Telegram-бота
    TELEGRAM_TOKEN = "8096091311:AAEaXfrruX9Rp1ZNZh_lrekrK9Ild0tzubk"

    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("confirm", confirm_payment))
    dp.add_handler(CommandHandler("code", get_code))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, choose_plan))

    updater.start_polling()
    updater.idle()

if name == 'main':
    main()
