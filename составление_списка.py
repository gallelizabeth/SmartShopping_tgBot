import logging
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5182243678:AAH315moUblzcJYSXYfzS57jIZxNUeVqDMU'
add_prod = []
shopping_list = ''
all_lists = dict()
done_address = False
creating = False
saving = False
writing_adrs = False
save = False
list_prod = []

# keyboard
save_items = [['Да', 'Нет']]
markup_1 = ReplyKeyboardMarkup(save_items, one_time_keyboard=False)


def start(update, context):
    update.message.reply_text("Привет! Я помогу Вам составить список покупок и найти нужный магазин")
    update.message.reply_text("Рекомендую задать свой адрес командой /setaddress для более качественного"
                              " пользования \n"
                              "Так же, ты сможешь управлять мной используя эти команды: \n"
                              "/editaddress – редактировать профиль \n"
                              "/makealist – собрать список \n"
                              "/foundshop – найти ближайший магазин \n"
                              "/editlist – редактировать список \n"
                              "нажмите /help , если вам понадобится помощь")


def write_address(update, context):
    global writing_adrs
    update.message.reply_text("Укажи адрес, к которому ты хочешь прокладывать маршруты")
    writing_adrs = True


def help_me(update, context):
    update.message.reply_text("Если у вас что-то не получается, попробуйте поменять регистр сообщения. "
                              "Если же проблема не исчезла, советуем обратиться в поддержку. \n"
                              "Приятной эксплуатации :)")


def create_list(update, context):
    global creating
    update.message.reply_text('Введи название продукта и его количество через пробел')
    update.message.reply_text('Когда закончишь, напиши СТОП')
    creating = True


def reaction(update, context):
    global shopping_list, creating, saving, all_lists, list_prod
    global writing_adrs, done_address, add_prod, save
    if creating:
        list_prod.append(update.message.text)
        if update.message.text != 'СТОП' and update.message.text != 'стоп':
            print(update.message.text)
        else:
            list_prod.pop(list_prod.index(list_prod[-1]))
            update.message.reply_text('Вот твой список:')
            for i in sorted(list_prod):
                if not i[-1].isalpha():
                    shopping_list = shopping_list + i + ' шт' + '\n'
                else:
                    shopping_list = shopping_list + i + '\n'
            update.message.reply_text(shopping_list)
            creating = False
            save_list(update, context, shopping_list)
    elif update.message.text == 'Да' and save:
        update.message.reply_text('Дай название списку')
        save = False
        saving = True
    elif update.message.text == 'Нет' and save:
        shopping_list = ''
        list_prod = []
        save = False
        update.message.reply_text('Список удален')
    elif saving:
        name = update.message.text
        all_lists[name] = shopping_list
        shopping_list = ''
        list_prod = []
        update.message.reply_text(f'Список сохранен как "{name}"')
        saving = False
    if writing_adrs:
        address = update.message.reply_text
        update.message.reply_text("Ты успешно установил адрес")
        writing_adrs = False
        done_address = True
        return address


def edit_list(update, context):
    global add_prod, shopping_list, list_edit
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
    list_edit = True


def save_list(update, context, saving_list):  # сохранение списка в бд
    global save
    update.message.reply_text("Ты хочешь сохранить список?", reply_markup=markup_1)
    save = True


def see_list(update, context):  # посмотреть список
    pass


def make_a_way(update, context):
    if done_address:
        update.message.reply_text('Поиск..')
    else:
        update.message.reply_text('Упс! Похоже, вы не указали адрес')


def edit_address(update, context):
    global writing_adrs
    update.message.reply_text("Укажи адрес на который ты хочешь сминить указанный")
    write_address(update, context)
    writing_adrs = True


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("setaddress", write_address))
    dp.add_handler(CommandHandler("makealist", create_list))
    dp.add_handler(CommandHandler("editlist", edit_list))
    dp.add_handler(MessageHandler(Filters.text, reaction))
    dp.add_handler(CommandHandler("editaddress", edit_address))
    dp.add_handler(CommandHandler("foundshop", make_a_way))
    dp.add_handler(CommandHandler("help", help_me))
    # "/editlist – редактировать список \n"

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
