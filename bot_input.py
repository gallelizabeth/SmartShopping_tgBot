import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5182243678:AAH315moUblzcJYSXYfzS57jIZxNUeVqDMU'

done_address = False
done_name = False


def start(update, context):
    update.message.reply_text(
        "Привет! Я помогу  тебе составить список покупок и найти нужный магазин, "
        "но для начала, зарегистрируйся с помощью команды /login \n"
        "если тебе понадобится помощь, вызови /help")


def login(update, context):
    do_username(update, context)


def do_username(update, context):
    global done_name
    update.message.reply_text("Введи как я могу к вам обращаться")
    name = update.message.text
    if name != '':
        done_name = True
        write_address(update, context)


def write_address(update, context):
    global done_address
    update.message.reply_text("Введи ваш адрес")
    address = update.message.text
    if address != '':
        done_address = True


def help_me(update, context):
    update.message.reply_text("Ты сможешь управлять мной используя эти команды: \n"
                              "/editprifile – редактировать профиль \n"
                              "/makealist – собрать список \n"
                              "/foundshop – найти ближайший магазин \n"
                              "нажми /help если тебе понадобиться помощь")


def make_a_list(update, context):
    update.message.reply_text('Составляем список..')


def make_a_way(update, context):
    if done_address:
        update.message.reply_text('Поиск..')
    else:
        update.message.reply_text('Упс! Похоже, вы не заполнили мини-профиль')


def edit_profile(update, context):
    if done_name:
        update.message.reply_text('Подключение к профилю..')
    else:
        update.message.reply_text('Упс! Похоже, вы не заполнили мини-профиль')


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("login", login))
    dp.add_handler(CommandHandler("editprifile", edit_profile))
    dp.add_handler(CommandHandler("makealist", make_a_list))
    dp.add_handler(CommandHandler("foundshop", make_a_way))
    dp.add_handler(CommandHandler("help", help_me))
    # "/editlist – редактировать список \n"

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
