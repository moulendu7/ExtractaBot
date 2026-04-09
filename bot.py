import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a PDF")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Upload PDF then ask")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)
    requests.get(f"{API_URL}/reset", params={"user_id": user_id})
    await update.message.reply_text("Reset done")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)

    await update.message.reply_text("Processing")

    file = await update.message.document.get_file()
    file_path = f"{user_id}.pdf"

    await file.download_to_drive(file_path)

    with open(file_path, "rb") as f:
        res = requests.post(
            f"{API_URL}/upload",
            files={"file": f},
            params={"user_id": user_id}
        )

    await update.message.reply_text("Uploaded")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)
    text = update.message.text

    await update.message.reply_text("Thinking")

    try:
        res = requests.get(
            f"{API_URL}/ask",
            params={"user_id": user_id, "question": text}
        )

        try:
            data = res.json()
            answer = data.get("answer", "error")
        except:
            answer = "server error"

        await update.message.reply_text(answer)

    except:
        await update.message.reply_text("failed")

async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❤️")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("reset", reset))

app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
app.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()