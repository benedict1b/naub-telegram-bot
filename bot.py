import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

if not TOKEN:
    print("❌ No token!")
    exit(1)

print("✅ Starting bot...")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎓 Welcome to NAUB AI! Type a question.")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": update.message.text}]
        }
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        if r.status_code == 200:
            reply = r.json()['choices'][0]['message']['content']
        else:
            reply = f"⚠️ Error: {r.status_code}"
    except Exception as e:
        reply = f"⚠️ Error: {str(e)}"
    await update.message.reply_text(reply)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle))
    print("✅ Bot running!")
    app.run_polling()

if __name__ == "__main__":
    main()
