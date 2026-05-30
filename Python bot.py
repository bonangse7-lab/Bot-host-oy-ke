import os
import logging
import subprocess
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from yt_dlp import YoutubeDL

# Update yt-dlp automatically
subprocess.run(["pip", "install", "--upgrade", "yt-dlp"], check=False)

# Load .env
load_dotenv()
TOKEN = os.getenv("8825680908:AAGtIitkyTME5DA8gFGquhA6KuOqfoNSML8")

# Download folder
DOWNLOAD_FOLDER = "./downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello!\n"
        "Send YouTube link\n"
        "I will send MP3 🎵"
    )


# Download audio from YouTube
async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ Please send valid YouTube link")
        return

    await update.message.reply_text("⏳ Downloading...")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
        "quiet": True,
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            title = info["title"]
            filename = os.path.join(
                DOWNLOAD_FOLDER,
                f"{title}.mp3"
            )

        # Send file
        with open(filename, "rb") as audio:
            await update.message.reply_audio(
                audio=audio,
                title=title,
            )

        # Delete after send
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        logging.error(e)
        await update.message.reply_text(
            f"❌ Error:\n{e}"
        )


def main():
    if not TOKEN:
        print("❌ Add TELEGRAM_BOT_TOKEN in .env")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            download_audio
        )
    )

    print("🤖 Bot running...")
    app.run_polling()


if name == "main":
    main()
