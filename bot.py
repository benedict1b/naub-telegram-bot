import os
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Try multiple possible key names
TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN") or os.getenv("TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_KEY")

if not TOKEN:
    print("❌ No Telegram token found!")
    exit(1)

if not GROQ_KEY:
    print("❌ No Groq API key found!")
    exit(1)

print("✅ Bot starting...")

async def get_ai_response(message: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": message}],
                    "temperature": 0.7,
                    "max_tokens": 800
                },
                timeout=30
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['choices'][0]['message']['content']
                return f"⚠️ Error: {resp.status}"
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎓 Welcome to NAUB AI Assistant! Ask me anything about NAUB.")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = await get_ai_response(update.message.text)
    await update.message.reply_text(response)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("✅ Bot is running!")
    app.run_polling()

if __name__ == "__main__":
    main()
