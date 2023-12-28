import telebot
from config import Config
import logging
import requests
import app.api.models.models as models

# logging
logger = logging.getLogger(__name__)

# tgbot
bot = telebot.TeleBot(Config.TG_BOT_TOKEN)

# /start handler
@bot.message_handler(commands=['start'])
def start_message(message):

  logger.info('Bot got "start" message')

  # message sample
  start_message = 'start_message'

  # collecting username and adding to db
  requests.post(f'{Config.API_HOST}/db/create_users/', json={"username": message.from_user.username})
  logger.info('Bot sent username into db')

  bot.send_message(message.chat.id, start_message)
  logger.info('Bot sent answer to "start" message')


def login(message):
  # getting token
  response = requests.post(f'{Config.API_HOST}/auth/login?username={message.from_user.username}')
  logger.info('Bot sent login request for a token')

  # preparing data to send 
  headers = {
    "Authorization": f"Bearer {response.json()['access_token']}"
  }
  
  return headers


# some text handler
@bot.message_handler(content_types='text')
def message_reply(message):

  logger.info('Bot got text message')

  data = {
    "text": message.text
  }
  
  # getting response with result
  response = requests.post(f'{Config.API_HOST}/summarizer/', json=data, headers=login(message))
  logger.info('Bot got response from summarizer')

  output = response.json()[0]['result']
  delta = response.json()[0]['delta']

  response = requests.put(f'{Config.API_HOST}/db/promts?delta={delta}', headers=login(message))

  bot.send_message(message.chat.id, output)
  logger.info('Bot sent answer to text message')


