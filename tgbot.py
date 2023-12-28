import app.tg.bot as tgbot
import logging

# logging
logging.getLogger().name = __name__
logging.basicConfig(filename='logs.log', filemode='a', level=logging.INFO, format='%(asctime)s - %(name)-14s - %(levelname)-8s - %(message)s')

# start tgbot
tgbot.bot.infinity_polling()