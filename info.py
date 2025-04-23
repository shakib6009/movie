from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
from bs4 import BeautifulSoup
import asyncio

BASE_URL = "https://movie.banglaflix.com"

# মুভি সার্চ করে রেজাল্ট ফেরত দেয়
def search_movies(query):
    url = f"{BASE_URL}/?s={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    movies = []
    results = soup.select("div.result-item") or soup.select("article")

    for item in results:
        title = item.select_one("h3 a, h2 a")
        if title:
            movie_title = title.get_text(strip=True)
            movie_link = title['href']
            movies.append(f"{movie_title}\n{movie_link}")

    return movies or ["কোনো মুভি পাওয়া যায়নি।"]

# /start কমান্ড
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("স্বাগতম! আপনি যেকোনো মুভির নাম লিখে সার্চ করতে পারেন।")

# সাধারণ টেক্সট হ্যান্ডলার
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text("অনুসন্ধান করা হচ্ছে...")
    results = search_movies(query)
    for result in results[:5]:  # প্রথম ৫টা দেখাবে
        await update.message.reply_text(result)

# মেইন ফাংশন
async def main():
    app = ApplicationBuilder().token("তোমার-বট-টোকেন").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    await app.run_polling()

# asyncio লুপ চালানো
if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
