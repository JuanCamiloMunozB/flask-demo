import os
import threading
from keepalive import app as flask_app
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from app.models.betting_adviser import BettingAdviser
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("TELEGRAM_TOKEN")

advisers = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola, soy tu asistente de apuestas deportivas. ¿Sobre qué deporte quieres apostar hoy? (fútbol o baloncesto)")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    advisers.pop(user_id, None)
    context.user_data.clear()
    await update.message.reply_text("🔁 Conversación reiniciada. ¿Sobre qué deporte quieres apostar hoy? (fútbol o baloncesto)")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()

    if text in ["reiniciar", "reset", "/reset", "volver a empezar"]:
        advisers.pop(user_id, None)
        context.user_data.clear()
        await update.message.reply_text("🔁 Conversación reiniciada. ¿Sobre qué deporte quieres apostar hoy? (fútbol o baloncesto)")
        return

    if user_id not in advisers:
        if "fútbol" in text or "futbol" in text:
            advisers[user_id] = BettingAdviser("soccer")
            facts = []
            response = advisers[user_id].get_betting_advice(facts)
            await update.message.reply_text(response["message"])
            if response.get("next_fact"):
                context.user_data["facts"] = facts
                context.user_data["next_fact"] = response["next_fact"]
        elif "basket" in text or "baloncesto" in text:
            advisers[user_id] = BettingAdviser("basketball")
            facts = []
            response = advisers[user_id].get_betting_advice(facts)
            await update.message.reply_text(response["message"])
            if response.get("next_fact"):
                context.user_data["facts"] = facts
                context.user_data["next_fact"] = response["next_fact"]
        else:
            await update.message.reply_text("Por favor escribe 'fútbol' o 'baloncesto' para comenzar.")
    else:
        facts = context.user_data.get("facts", [])
        next_fact = context.user_data.get("next_fact")

        if next_fact:
            facts.append({next_fact: text})

        # Send processing message
        loading_msg = await update.message.reply_text("⏳ Procesando información...")

        response = advisers[user_id].get_betting_advice(facts)

        if response.get("next_fact"):
            context.user_data["facts"] = facts
            context.user_data["next_fact"] = response["next_fact"]
            try:
                await loading_msg.edit_text(response["message"])
            except Exception:
                await update.message.reply_text(response["message"])
        else:
            advisers.pop(user_id)
            context.user_data.clear()
            try:
                await loading_msg.edit_text(response["message"])
            except Exception:
                await update.message.reply_text(response["message"])


def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
