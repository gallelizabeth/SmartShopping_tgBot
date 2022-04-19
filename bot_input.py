import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

# Запускаем логгирование
from составление_списка import save_list

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5182243678:AAH315moUblzcJYSXYfzS57jIZxNUeVqDMU'

done_address = False
add_prod = []
shopping_list = ''


def start(update, context):
    update.message.reply_text("Привет! Я помогу тебе составить список покупок и найти нужный магазин")
    update.message.reply_text("Рекомендую задать свой адрес командой /setaddress, для более качественного"
                              " использования \n"
                              "Так же, ты сможешь управлять мной используя эти команды: \n"
                              "/editaddress – изменить адрес \n"
                              "/makealist – собрать список \n"
                              "/found shop – найти ближайший магазин \n"
                              "/editlist – редактировать список \n"
                              "нажми /help если тебе понадобиться помощь")


def write_address(update, context):
    global done_address
    update.message.reply_text("Укажи адрес к которому ты хочешь прокладывать маршруты")
    address = update.message.text
    if 'foundshop' not in address:
        done_address = True
        update.message.reply_text("Ты успешно установил адрес")
    return address


def help_me(update, context):
    update.message.reply_text("Если у тебя что-то не получается, попробуй поменять регистр сообщения. "
                              "Если же проблема не исчезла, советуем обратиться в поддержку \n"
                              "Приятной эксплуатации :)")


def make_a_list(update, context):
    import sqlite3
    con = sqlite3.connect("lists_db.db")
    cur = con.cursor()
    # quary = """INSERT INTO saves(name_of_list, list) VALUES (""" + str(name) + """,""" + str(
    # list_prod) + """)"""
    # cur.execute(quary)
    con.commit()
    con.close()
    update.message.reply_text('Составляем список..')


def edit_list(update, context):
    global add_prod, shopping_list
    update.message.reply_text('Укажи название списка в который ты хочешь добавить продукт(ы)')
    list_name = update.message.text
    update.message.reply_text('Укажи продукты которые ты хочешь добавить')
    update.message.reply_text('Когда закончишь, напиши СТОП')
    add_prod.append(update.message.text)
    if update.message.text != 'СТОП' and update.message.text != 'стоп':
        print(update.message.text)
    else:
        add_prod.pop(add_prod.index(add_prod[-1]))
        update.message.reply_text('Вот твой список:')
        for i in sorted(add_prod):
            if not i[-1].isalpha():
                shopping_list = shopping_list + i + ' шт' + '\n'
            else:
                shopping_list = shopping_list + i + '\n'
        update.message.reply_text(shopping_list)
        save_list(update, context, shopping_list)
    import sqlite3
    con = sqlite3.connect("lists_db.db")
    cur = con.cursor()
    quary = """INSERT INTO saves(list) VALUES (""" + str(add_prod) + """)"""
    saved_list = """SELECT list FROM saves WHERE name_of_list = (""" + str(list_name) + """)"""
    cur.execute(quary)
    con.commit()
    con.close()
    update.message.reply_text(saved_list)


def find_shop(update, context):
    if done_address:
        update.message.reply_text('Поиск..')
    else:
        update.message.reply_text('Упс! Похоже, ты не указал адрес')


def edit_address(update, context):
    global writing_adrs
    writing_adrs = False
    update.message.reply_text("Укажи адрес на который ты хочешь сминить указанный")
    writing_adrs = True


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("setaddress", write_address))
    dp.add_handler(CommandHandler("editaddress", edit_address))
    dp.add_handler(CommandHandler("makealist", make_a_list))
    dp.add_handler(CommandHandler("editlist", edit_list))
    dp.add_handler(CommandHandler("foundshop", find_shop))
    dp.add_handler(CommandHandler("help", help_me))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
