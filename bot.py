import os
import requests
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# =============================================
# CONFIGURATION - Load from .env file
# =============================================

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Check if secrets are set
if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    print("❌ ERROR: Missing environment variables!")
    print("Make sure .env file exists with TELEGRAM_TOKEN and GROQ_API_KEY")
    exit(1)

print("✅ Environment variables loaded successfully!")

# =============================================
# GROQ API CALL
# =============================================

def get_ai_response(message):
    """Send message to Groq API and get response"""
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system",
                    "content": "You are NAUB AI, a helpful assistant for students of Nigerian Army University Biu. Give brief, accurate answers."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            "temperature": 0.7,
            "max_tokens": 800
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"⚠️ Error: {response.status_code}. Please try again."
            
    except requests.exceptions.Timeout:
        return "⚠️ Connection timed out. Please try again."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# =============================================
# OFFLINE RESPONSES (Fallback)
# =============================================

def get_offline_response(query):
    q = query.lower()
    
    if "gpa" in q:
        return "📊 GPA is calculated by multiplying grade points by credit units, summing, and dividing by total credits."
    elif "registration" in q:
        return "📅 Registration starts in September. Check the academic calendar for exact dates."
    elif "library" in q:
        return "📚 The library is in Block A, Main Academic Building."
    elif "hostel" in q:
        return "🏠 Hostel rules: No visitors after 10PM, no cooking in rooms, maintain cleanliness."
    elif "fee" in q or "school" in q:
        return "💰 Science: ₦84,500 | Arts: ₦64,500"
    elif "admission" in q or "cut off" in q:
        return "🎓 UTME cut-off: 180. Candidates with 160+ are eligible for Post-UTME."
    else:
        return None

# =============================================
# TELEGRAM BOT HANDLERS
# =============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """
🎓 **Welcome to NAUB AI Assistant!**

I'm your AI assistant for Nigerian Army University Biu.

**I can help you with:**
• 📊 GPA Calculation
• 📅 Registration Dates
• 📚 Library Information
• 🏠 Hostel Rules
• 💰 School Fees
• 🎓 Admissions & Cut-off Marks
• 📍 Campus Locations

Just type your question and I'll help! 🚀
"""
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
🤖 **NAUB AI Help**

**Simply type your question**, for example:
• "How do I calculate my GPA?"
• "When does registration start?"
• "Where is the library?"
• "What are the hostel rules?"
• "How much are school fees?"

**Commands:**
/start - Welcome message
/help - Show this help
/about - About NAUB AI

**Status:** 🟢 Online
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    about_text = """
📖 **About NAUB AI**

NAUB AI is an intelligent assistant built for students of Nigerian Army University Biu.

**Features:**
• AI-powered chat using Groq
• Offline responses for common questions
• Available 24/7 on Telegram

**Developed by:** NAUB Tech Team
**Version:** 1.0.0

💡 Connect to the internet for full AI responses.
"""
    await update.message.reply_text(about_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages"""
    user_message = update.message.text
    await update.message.reply_chat_action("typing")
    
    # Try AI response first
    response = get_ai_response(user_message)
    
    # If AI fails or returns error, try offline
    if "Error" in response or "timed out" in response:
        offline_response = get_offline_response(user_message)
        if offline_response:
            response = offline_response + "\n\n💡 Using offline mode."
    
    await update.message.reply_text(response)

# =============================================
# MAIN
# =============================================

def main():
    print("🤖 NAUB AI Telegram Bot Starting...")
    
    # Create application with increased timeout
    application = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .connect_timeout(30.0)   # Increase connection timeout
        .read_timeout(30.0)      # Increase read timeout
        .build()
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start bot with reduced poll interval
    print("✅ Bot is running! Press Ctrl+C to stop.")
    application.run_polling(poll_interval=1.0)

if __name__ == "__main__":
    main()
