import logging
import telegram
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5182243678:AAH315moUblzcJYSXYfzS57jIZxNUeVqDMU'
list_prod = []
shopping_list = ''
all_lists = dict()
done_address = False
creating = False
saving = False
writing_adrs = False

# keyboard
save_items = [['Да', 'Нет']]
markup_1 = ReplyKeyboardMarkup(save_items, one_time_keyboard=True)


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
    global writing_adrs
    update.message.reply_text("Укажи адрес к которому ты хочешь прокладывать маршруты")
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
    global shopping_list, creating, saving, all_lists
    global writing_adrs, done_address
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
    elif update.message.text == 'Да' and not creating:
        update.message.reply_text('Дай название списку')
        saving = True
    elif update.message.text == 'Нет' and not creating:
        shopping_list = ''
        update.message.reply_text('Список удален')
    elif saving:
        name = update.message.text
        all_lists[name] = shopping_list
        shopping_list = ''
        update.message.reply_text(f'Список сохранен как "{name}"')
        saving = False
    if writing_adrs:
        address = update.message.reply_text
        update.message.reply_text("Ты успешно установил адрес")
        writing_adrs = False
        done_address = True
        return address


def save_list(update, context, saving_list):  # сохранение списка в бд
    global saving
    update.message.reply_text("Ты хочешь сохранить список?", reply_markup=markup_1)


def see_list(update, context):  # посмотреть список
    pass


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
    dp.add_handler(CommandHandler("makealist", create_list))
    dp.add_handler(MessageHandler(Filters.text, reaction))
    dp.add_handler(CommandHandler("editaddress", edit_address))
    dp.add_handler(CommandHandler("foundshop", make_a_way))
    dp.add_handler(CommandHandler("help", help_me))
    # "/editlist – редактировать список \n"

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
