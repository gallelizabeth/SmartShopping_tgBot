import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5182243678:AAH315moUblzcJYSXYfzS57jIZxNUeVqDMU'

def start(update, context):
    update.message.reply_text(
        "Привет! Я посчитаю количество символов твоего сообщений. Напишите мне что-нибудь, и я пришлю тебе число!")

def counter(update, context):
    answer = 'В вашем сообщении '
    if len(update.message.text) == 1:
        update.message.reply_text(answer + str(len(update.message.text)) + ' символ.')
    elif 3 <= len(update.message.text) <= 5:
        update.message.reply_text(answer + str(len(update.message.text)) + ' символа.')
    else:
        update.message.reply_text(answer + str(len(update.message.text)) + ' символов.')


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    # После регистрации обработчика в диспетчере
    # эта функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.
    text_handler = MessageHandler(Filters.text, counter)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(text_handler)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
