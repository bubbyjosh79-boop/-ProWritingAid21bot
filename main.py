import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load secret environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AI_API_KEY = os.getenv("AI_API_KEY")

# Initialize AI Client
ai_client = OpenAI(api_key=AI_API_KEY)

# Define the /start command greeting
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 **Welcome to ProWritingAid21 Bot!**\n\n"
        "I am your dedicated AI writing assistant and developmental editor. "
        "Send me any text (essays, blog posts, stories, or professional emails), and I will analyze it for:\n"
        "• Grammar & Readability\n"
        "• Structural Flow & Tone\n"
        "• Structural Improvements (with an improved rewrite!)\n\n"
        "Just paste your text below to begin!",
        parse_mode="Markdown"
    )

# The core writing critique and optimization function
async def proofread_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # Visual cue that the bot is thinking/processing
    await update.message.reply_chat_action("typing")
    
    # Elite structural editing prompt
    editing_prompt = f"""
    You are an elite copyeditor and literacy coach. Analyze and optimize the following text. 
    Provide your response in a beautiful, structured format.
    
    TEXT TO REVIEW:
    "{user_text}"
    
    Provide exactly 3 sections:
    1. 🔍 **Quick Critique**: 2-3 bullet points identifying issues with tone, syntax, or passive voice.
    2. ✨ **The Polish**: An elegant, highly improved version of the text that retains the original intent but elevates the delivery.
    3. 💡 **Pro-Tip**: One actionable rule of thumb the writer can take away for future work.
    """
    
    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini", # High-speed, high-accuracy model for text transformation
            messages=[{"role": "user", "content": editing_prompt}],
            temperature=0.3 # Lower temperature ensures stricter adherence to grammar rules
        )
        ai_analysis = response.choices[0].message.content
        await update.message.reply_text(ai_analysis, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Editing framework encountered an issue: {e}")
        await update.message.reply_text("❌ I encountered an issue analyzing your text. Please ensure my API keys are configured properly.")

def main():
    if not TOKEN:
        logger.critical("TELEGRAM_BOT_TOKEN environment variable is missing!")
        return

    # Build the bot application using long polling
    application = Application.builder().token(TOKEN).build()

    # Link paths/commands to functions
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, proofread_text))

    logger.info("ProWritingAid21bot initialized. Polling started...")
    
    # drop_pending_updates ignores messages sent while the bot was offline to avoid backlogs
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
