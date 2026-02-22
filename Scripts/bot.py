import os
import asyncio
import logging
import yt_dlp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile
from dotenv import load_dotenv

# Load environment variables
load_dotenv('Credentials.env')

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Directory for downloads
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def download_video(url):
    ydl_opts = {
        'format': 'best[filesize<50M]/bestvideo[filesize<45M]+bestaudio/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            filename = ydl.prepare_filename(info)
            
            # If the filename extension changed during merging, we need the actual file
            if not os.path.exists(filename):
                base = os.path.splitext(filename)[0]
                for ext in ['mp4', 'mkv', 'webm']:
                    if os.path.exists(f"{base}.{ext}"):
                        filename = f"{base}.{ext}"
                        break
            return filename
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            return None

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Пришли мне ссылку на видео из Instagram, Twitter, TikTok или другого сервиса, и я скачаю его для тебя.")

@dp.message(F.text.regexp(r'https?://[^\s]+'))
async def handle_url(message: types.Message):
    url = message.text.strip()
    status_msg = await message.answer("🔍 Обрабатываю ссылку...")
    
    try:
        loop = asyncio.get_event_loop()
        filename = await loop.run_in_executor(None, download_video, url)
        
        if filename and os.path.exists(filename):
            await status_msg.edit_text(" Загружаю видео в Telegram...")
            video = FSInputFile(filename)
            await message.reply_video(video)
            await status_msg.delete()
            os.remove(filename)
        else:
            await status_msg.edit_text("❌ Не удалось скачать видео.")
    except Exception as e:
        logger.error(f"Error handling URL {url}: {e}")
        await status_msg.edit_text(f"⚠️ Ошибка: {str(e)[:100]}")

async def main():
    logger.info("Cleaning up commands and starting bot...")
    await bot.delete_my_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
