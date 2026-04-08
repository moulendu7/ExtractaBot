import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send a PDF to begin.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📘 Upload PDF → Ask questions\n\n/start\n/help\n/reset"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)
    requests.get(f"{API_URL}/reset", params={"user_id": user_id})
    await update.message.reply_text("🔄 Upload new PDF.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)

    await update.message.reply_text("⏳ Processing PDF...")

    file = await update.message.document.get_file()
    file_path = f"{user_id}.pdf"

    await file.download_to_drive(file_path)

    with open(file_path, "rb") as f:
        res = requests.post(
            f"{API_URL}/upload",
            files={"file": f},
            params={"user_id": user_id}
        )

    print("UPLOAD:", res.text)

    await update.message.reply_text("✅ PDF uploaded. Ask questions.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)
    text = update.message.text

    if text.lower() in ["hi", "hello"]:
        await update.message.reply_text("👋 Hello!")
        return

    await update.message.reply_text("⏳ Thinking...")

    res = requests.get(
        f"{API_URL}/ask",
        params={"user_id": user_id, "question": text}
    )

    answer = res.json().get("answer", "⚠️ Error")

    await update.message.reply_text(answer)

async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❤️")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("reset", reset))

app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
app.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🚀 Bot running...")

app.run_polling()