import logging

import telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = 'TOKEN'
list_prod = []
shopping_list = ''
all_lists = dict()


def start(update, context):
    update.message.reply_text("Привет! Я помогу Вам составить список покупок и найти нужный магазин")
    update.message.reply_text("Рекомендую задать свой адрес командой /setaddress для более качественного"
                              " пользования \n"
                              "Так же, ты сможешь управлять мной используя эти команды: \n"
                              "/editaddress – редактировать профиль \n"
                              "/makealist – собрать список \n"
                              "/foundshop – найти ближайший магазин \n"
                              "нажмите /help , если вам понадобится помощь")


def create_list(update, context):
    update.message.reply_text('Введи название продукта и его количество через пробел')
    update.message.reply_text('Когда закончишь, напиши СТОП')


def add_item(update, context):
    global shopping_list
    list_prod.append(update.message.text)
    if update.message.text != 'СТОП':
        print(update.message.text)
    else:
        list_prod.pop(list_prod.index(list_prod[-1]))
        update.message.reply_text('Вот твой список:')
        for i in sorted(list_prod):
            if not i[-1].isalpha():
                shopping_list = shopping_list + i + ' шт' + '\n'
            else:
                shopping_list = shopping_list + i + '\n'
        save_list(shopping_list)
        update.message.reply_text(shopping_list)


def save_list(saving_list):
    # сохранение в базу данных или куда-то там еще


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("makealist", create_list))
    dp.add_handler(MessageHandler(Filters.text, add_item))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()