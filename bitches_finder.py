import os
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    BotCommand
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from time import time

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 🔐 ТВОЇ ДАНІ
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 588956185  # <-- заміни на свій Telegram ID

logger.info(f"Bot token loaded: {'Yes' if BOT_TOKEN else 'No'}")
logger.info(f"Admin ID: {ADMIN_ID}")

# Стан користувачів
user_states = {}
user_answers = {}
last_message_time = {}

# Правильні відповіді
correct_answers = {
    1: "Дівчина",
    2: ["18-25", "26-35"],
    3: ["Гетеро", "Бісексуал"],
    4: ["Серйозні стосунки", "Романтичні побачення", "Дружба"],
    5: "Так",
    6: "Так",
    7: "Так",
    8: "Так",
    9: "Так",
    10: ["Позитивно", "Мало знайомі"],
    11: ["Позитивно", "Мало знайомі"],
    12: ["Позитивно", "Мало знайомі"],
    13: ["Позитивно", "Мало знайомі"],
    14: "Так"
}

# Питання
questions = {
    1: {"text": "Оберіть свою стать:", "options": ["Дівчина", "Хлопець", "Інше"]},
    2: {"text": "Ваш вік?", "options": ["18-25", "26-35", "Менше 18", "Більше 35"]},
    3: {"text": "Ваша сексуальна орієнтація?", "options": ["Гетеро", "Гомо", "Бісексуал", "Інше"]},
    4: {"text": "Ваша мета знайомства?", "options": ["Серйозні стосунки", "Романтичні побачення", "Дружба"]},
    5: {"text": "Ви готові до смішнявок?", "options": ["Так", "Ні"]},
    6: {"text": "Ви зі Львову?", "options": ["Так", "Ні"]},
    7: {"text": "Ви готові до реальної зустрічі?", "options": ["Так", "Ні"]},
    8: {"text": "Ви готові на реальній зустрічі взаємодіяти з несміливим і мовчазним хлопцем? (Це я, мені потрібен час на розкачку)", "options": ["Так", "Ні"]},
    9: {"text": "Ви готові до спілкування з людиною, яка може бути дивною?", "options": ["Так", "Ні"]},
    10: {"text": "Як ви сприймаєте настільні ігри?", "options": ["Позитивно", "Негативно", "Мало знайомі"]},
    11: {"text": "Як ви ставитесь до Настільно-Рольових Ігор?", "options": ["Позитивно", "Негативно", "Мало знайомі"]},
    12: {"text": "Як ви ставитесь до комп'ютерних ігор?", "options": ["Позитивно", "Негативно", "Мало знайомі"]},
    13: {"text": "Як ви ставитесь до аніме?", "options": ["Позитивно", "Негативно", "Мало знайомі"]},
    14: {"text": "Чи готові ви до знайомства з вищезначеними інтересами, якщо ще не знайомі?", "options": ["Так", "Ні"]},
    15: {"text": "Напишіть кілька слів про себе, щоб я міг краще вас зрозуміти:", "options": None}
}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        logger.info(f"User {user_id} started the bot")
        
        now = time()
        if user_id in last_message_time and now - last_message_time[user_id] < 0.3:
            return
        last_message_time[user_id] = now

        chat_id = update.effective_chat.id
        user_states[chat_id] = 1
        user_answers[chat_id] = {}

        reply_markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton("/start")],
                [KeyboardButton("/help"), KeyboardButton("/about")]
            ],
            resize_keyboard=True
        )

        await context.bot.send_message(
            chat_id=chat_id,
            text="Ласкаво просимо до Bitches Finder\nНатисни /start, щоб почати!",
            reply_markup=reply_markup
        )
        await send_question(chat_id, context, question_number=1)
        logger.info(f"Successfully sent start message to user {user_id}")
    except Exception as e:
        logger.error(f"Error in start command: {e}")

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.info(f"User {update.effective_user.id} requested help")
        await update.message.reply_text("Я бот для пошуку сумісної дівчини. Почни з /start")
    except Exception as e:
        logger.error(f"Error in help command: {e}")

# /about
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.info(f"User {update.effective_user.id} requested about")
        await update.message.reply_text("Bitches Finder — експериментальний Telegram-бот для пошуку альтушки власнику бота.")
    except Exception as e:
        logger.error(f"Error in about command: {e}")

# Команди меню
async def setup_commands(app):
    try:
        await app.bot.set_my_commands([
            BotCommand("start", "Почати опитування"),
            BotCommand("help", "Допомога та інструкція"),
            BotCommand("about", "Інформація про бота")
        ])
        logger.info("Bot commands set successfully")
    except Exception as e:
        logger.error(f"Error setting up commands: {e}")

# Питання
async def send_question(chat_id, context, question_number):
    try:
        logger.info(f"Sending question {question_number} to chat {chat_id}")
        q = questions[question_number]
        user_states[chat_id] = question_number

        if chat_id not in user_answers:
            user_answers[chat_id] = {}

        if q["options"]:
            buttons = [
                [InlineKeyboardButton(text=opt, callback_data=f"{question_number}:{opt}")]
                for opt in q["options"]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await context.bot.send_message(chat_id=chat_id, text=q["text"], reply_markup=reply_markup)
        else:
            await context.bot.send_message(chat_id=chat_id, text=q["text"])
        
        logger.info(f"Question {question_number} sent successfully to chat {chat_id}")
    except Exception as e:
        logger.error(f"Error sending question {question_number} to chat {chat_id}: {e}")

# Обробка кнопок
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        user_id = query.from_user.id
        logger.info(f"User {user_id} clicked button: {query.data}")
        
        now = time()
        if user_id in last_message_time and now - last_message_time[user_id] < 0.3:
            return
        last_message_time[user_id] = now

        await query.answer()
        data = query.data
        q_num_str, answer = data.split(":", 1)
        q_num = int(q_num_str)
        chat_id = query.message.chat_id
        user = query.from_user

        correct = correct_answers.get(q_num, [])
        is_correct = answer in correct if isinstance(correct, list) else answer == correct

        logger.info(f"User {user_id} answered Q{q_num}: {answer}, correct: {is_correct}")

        if is_correct:
            if chat_id not in user_answers:
                user_answers[chat_id] = {}
            user_answers[chat_id][q_num] = answer

            next_q = q_num + 1
            if next_q in questions:
                await send_question(chat_id, context, next_q)
            else:
                await query.edit_message_text("Дякую за проходження! Твої відповіді відправлені власнику бота. Можете написати йому в особисті повідомлення, якщо хочете поспілкуватись. Нікнейм: @TrueSifon")

                await context.bot.send_animation(
                    chat_id=chat_id,
                    animation="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExOXJ4ZmRkMHN0ajhtZm1vYWphOGxwNmFramp3cWhoa2l0NGE5bTczMCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5jT0jaNDsM6Ik7X9yq/giphy.gif"
                )
        else:
            await query.edit_message_text("Опитування завершено. Ви нам не підходите 😔")
            await context.bot.send_animation(
                chat_id=chat_id,
                animation="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExeGZneTdjcG40anA4aGhzN2ptaDRvcHI1dWhhdnQxNWlzb2pobGgzdSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/IT6kBZ1k5oEeI/giphy.gif"
            )
    except Exception as e:
        logger.error(f"Error handling callback query: {e}")

# Обробка текстової відповіді
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        logger.info(f"User {user_id} sent text message: {update.message.text}")
        
        now = time()
        if user_id in last_message_time and now - last_message_time[user_id] < 0.3:
            return
        last_message_time[user_id] = now

        chat_id = update.effective_chat.id  
        user = update.effective_user
        text = update.message.text
        current_q = user_states.get(chat_id)

        if current_q == 15:
            user_answers[chat_id][15] = text

            answers_text = "\n".join(
                f"Q{q_num}: {questions[q_num]['text']}\n➡️ {user_answers[chat_id].get(q_num, '-')}\n"
                for q_num in sorted(user_answers[chat_id])
            )

            msg = (
                f"✅ Хтось пройшов бот:\n"
                f"Ім'я: {user.first_name or ''} {user.last_name or ''}\n"
                f"Username: @{user.username or '—'}\n"
                f"ID: {user.id}\n\n"
                f"{answers_text}"
            )

            await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
            await update.message.reply_text("Дякую за проходження! Твої відповіді відправлені власнику бота. Можете написати йому в особисті повідомлення, якщо хочете поспілкуватись. Нікнейм: @TrueSifon")
            await context.bot.send_animation(
                chat_id=chat_id,
                animation="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExOXJ4ZmRkMHN0ajhtZm1vYWphOGxwNmFramp3cWhoa2l0NGE5bTczMCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5jT0jaNDsM6Ik7X9yq/giphy.gif"
            )

            del user_states[chat_id]
            user_answers.pop(chat_id, None)
            logger.info(f"User {user_id} completed the survey")
    except Exception as e:
        logger.error(f"Error handling text message: {e}")

# ▶️ Запуск
if __name__ == "__main__":
    logger.info("Starting bot...")
    
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables!")
        exit(1)
    
    try:
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Додаємо обробники
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("about", about_command))
        app.add_handler(CallbackQueryHandler(handle_answer))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        
        # Налаштовуємо команди
        app.post_init = setup_commands
        
        logger.info("Bot handlers added, starting polling...")
        print("Connected!")  # Це повідомлення, яке ви бачите в логах
        
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        exit(1)
