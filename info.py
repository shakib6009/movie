import telegram
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler
from telegram.ext.filters import BaseFilter
import logging
import tmdbsimple as tmdb

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# TMDB API Key
tmdb.API_KEY = '6db3367018a3783ce9fccff017a9fb12'

# Telegram Bot Token
TELEGRAM_TOKEN = "7535439008:AAFYXGLjbanDwTAatoBg3ILPQUcqgKVt2MM"

BASE_URL = "https://movie.banglafilx.com/watch/"

class SearchFilter(BaseFilter):
    def filter(self, message):
        return bool(message.text and message.text.startswith("#search") and len(message.text.split()) > 1)

search_filter = SearchFilter()

async def movie(update, context):
    if update.message and update.message.text:
        if update.message.text.startswith("#search"):
            try:
                movie_name = update.message.text.split(' ', 1)[1]
                logger.info(f"Movie name before replace: {movie_name}")
                movie_name_hyphenated = movie_name.replace(" ", "-")
                logger.info(f"Movie name after replace: {movie_name_hyphenated}")

                # TMDB থেকে মুভির তথ্য সংগ্রহ করুন
                search = tmdb.Search()
                response = search.movie(query=movie_name)

                if search.results:
                    movie = search.results[0]
                    movie_id = movie['id']
                    movie_title = movie['title']
                    movie_rating = movie['vote_average']
                    movie_poster_path = movie['poster_path']
                    movie_poster_url = None
                    if movie_poster_path:
                        movie_poster_url = f"https://image.tmdb.org/t/p/w500{movie_poster_path}"

                    movie_link = BASE_URL + movie_name_hyphenated + ".html"
                    message_text = f"🎬 Title: {movie_title}\n⭐ Rating: {movie_rating}\n🎭 Genres: {', '.join([genre['name'] for genre in movie['genres']]) if 'genres' in movie else 'N/A'}\n🗓️ Release Date: {movie['release_date'] if 'release_date' in movie else 'N/A'}\n{movie['overview'] if 'overview' in movie else 'N/A'}\nPlay and Download full movie\n\n{movie_link}\n\n🔥 Hi users thanks for join\n🌟 উপরের লিংক থেকে আপনার মুভিটি প্লে বা ডাউনলোড করুন। আরো আপডেট পেতে আমাদের টেলিগ্রাম গুরুপ এ join হোন, লিংক,, https://t.me/banglafilx2025\nযদি সঠিক মুভি/সিরিজ না পেয়ে থাকেন, তবে আবার 🎁 সঠিক নাম লিখে সার্চ দিন।\n🔎 যেমনঃ #search borbaad"
                    if movie_poster_url:
                        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=movie_poster_url, caption=message_text)
                    else:
                        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
                else:
                    await context.bot.send_message(chat_id=update.effective_chat.id, text="Movie not found on TMDB. Please check the movie name or try again later.")

            except IndexError:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a movie name.")
        else:
            return
    else:
        logger.warning("Received a message without text")
        return

async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a movie bot, send me a movie name to find the link!")

async def photo_handler(update: telegram.Update, context: telegram.ext.CallbackContext):
    logger.info("photo_handler called")
    if update.message.photo:
        logger.info("photo detected")
        message_text = "Hello users. Thanks for sending the image. We will search and update you as soon as possible."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
    else:
        logger.info("no photo detected")
        return

async def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    try:
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(search_filter, movie))
        photo_handler_instance = MessageHandler(telegram.ext.filters.PHOTO, photo_handler)
        application.add_handler(photo_handler_instance)
        logger.info(f"Photo handler added: {photo_handler_instance}")

        application.add_error_handler(error)

        application.run_polling()
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)

if __name__ == '__main__':
    main()
