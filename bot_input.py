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
        "Привет! Я помогу вам составить список покупок и найти нужный магазин :) "
        "Давай приступим!")
    login(update, context)


def login(update, context):
    update.message.reply_text("Для начала, давай зарегестрируемся."
                              "Введи как к тебе обращаться и ваш адрес через точку с запятой (;)")
    input_text = update.message.text
    name, adress = input_text.split(';')
    search(update, context)


def search(update, context):
    update.message.reply_text("Теперь, выбери что хочешь сделать далее: "
                              "составить список, редактировать профиль, маршрут до магазина")
    check_answer(update, context)



def check_answer(update, context):
    input_text = update.message.text
    if input_text == 'составить список':
        make_a_list(update, context)
    elif input_text == 'редактировать профиль':
        make_a_way(update, context)
    elif input_text == 'маршрут до магазина':
        edit_profil(update, context)


def make_a_list(update, context):
    update.message.reply_text('Составляем список..')


def make_a_way(update, context):
    update.message.reply_text('Подключение к профилю..')


def edit_profil(update, context):
    update.message.reply_text('Поиск..')


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    # После регистрации обработчика в диспетчере
    # эта функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.
    text_handler = MessageHandler(Filters.text, search)
    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(text_handler)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
