import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5182243678:AAH315moUblzcJYSXYfzS57jIZxNUeVqDMU'

done_address = False


def start(update, context):
    update.message.reply_text("Привет! Я помогу Вам составить список покупок и найти нужный магазин")
    update.message.reply_text("Рекомендую задать свой адрес командой /setaddress для более качественного"
                              " пользования \n"
                              "Так же, ты сможешь управлять мной используя эти команды: \n"
                              "/editaddress – редактировать профиль \n"
                              "/makealist – собрать список \n"
                              "/foundshop – найти ближайший магазин \n"
                              "нажмите /help , если вам понадобится помощь")


def write_address(update, context):
    global done_address
    update.message.reply_text("Укажите ваш адрес")
    address = update.message.text
    if address[0] != '/':
        done_address = True
    return address


def help_me(update, context):
    update.message.reply_text("Если у вас что-то не получается, попробуйте поменять регистр сообщения. "
                              "Если же проблема не исчезла, советуем обратиться в поддержку. \n"
                              "Приятной эксплуатации :)")


def make_a_list(update, context):
    update.message.reply_text('Составляем список..')


def make_a_way(update, context):
    if done_address:
        update.message.reply_text('Поиск..')
    else:
        update.message.reply_text('Упс! Похоже, вы не указали адрес')


def edit_address(update, context):
    if done_address:
        update.message.reply_text('Подключение к профилю..')
    else:
        update.message.reply_text('Упс! Похоже, вы не указали адрес')


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("setaddress", write_address))
    dp.add_handler(CommandHandler("editaddress", edit_address))
    dp.add_handler(CommandHandler("makealist", make_a_list))
    dp.add_handler(CommandHandler("foundshop", make_a_way))
    dp.add_handler(CommandHandler("help", help_me))
    # "/editlist – редактировать список \n"

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
