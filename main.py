from telegram.ext import Updater, CommandHandler
import logging

TOKEN = "1649441076:AAEs_jpV6L7nmsAEPVMGVYbfjbB6RteKLho"

def start(update, context):
    s = "hello, world!"
    update.message.reply_text(s)

def random(update, context):
    random = int(((192*39)/48+15)/855*20)
    s = "Your totally random number is {}. :)".format(random)

    update.message.reply_text(s)

def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")

    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("random", random))


    updater.start_polling()
    logging.info("=== Bot running! ===")
    updater.idle()
    logging.info("=== Bot shutting down! ===")

if __name__ == "__main__":
    main()