import logging

import requests
import telegram
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5349979559:AAHcXnyvYcT_ETNfqlJiJNC3uDjicwmU3mM'

add_prod = []
shopping_list = ''
address = ''
coordinates_shop = ''
all_lists = dict()
done_address = False
creating = False
saving = False
writing_adrs = False
save = False
list_prod = []
check = False
add_to_list = False
del_from_list = False
del_list = False
route = True
to_map = False

bot = telegram.Bot(TOKEN)

# keyboard
save_items = [['Да', 'Нет']]
check_list = [['Добавить элемент', 'Удалить элемент', 'Удалить список']]
markup_1 = ReplyKeyboardMarkup(save_items, one_time_keyboard=True)
markup_list = ReplyKeyboardMarkup(check_list, one_time_keyboard=True)


def start(update, context):
    update.message.reply_text("Привет! Я помогу тебе составить список покупок и найти нужный магазин")
    update.message.reply_text("Рекомендую задать свой адрес командой /setaddress для более качественного"
                              " пользования \n"
                              "Также ты сможешь управлять мной, используя эти команды: \n"
                              "/makealist – собрать список \n"
                              "/findshop – найти ближайший магазин \n"
                              "/editlist – редактировать список \n"
                              "/mylist – получить список \n"
                              "нажмите /help , если тебе понадобится помощь")


def write_address(update, context):
    global writing_adrs
    update.message.reply_text("Укажи адрес, рядом с которым мы будем искать магазин")
    writing_adrs = True


def help_me(update, context):
    update.message.reply_text("Если у тебя что-то не получается, попробуйте поменять регистр сообщения. "
                              "Если же проблема не исчезла, советуем обратиться в поддержку. \n"
                              "Приятной эксплуатации :)")


def create_list(update, context):
    global creating
    update.message.reply_text('Введи название продукта и его количество через пробел')
    update.message.reply_text('Когда закончишь, напиши СТОП')
    creating = True


def reaction(update, context):
    global shopping_list, creating, saving, all_lists, list_prod, route, address, coordinates_shop
    global writing_adrs, done_address, add_prod, save, check, add_to_list, del_from_list, del_list
    if creating:
        list_prod.append(update.message.text)
        if update.message.text == 'СТОП' or update.message.text == 'стоп' or update.message.text == 'Стоп':
            list_prod.pop(list_prod.index(list_prod[-1]))
            update.message.reply_text('Вот твой список:')
            for i in list_prod:
                if not i[-1].isalpha():
                    shopping_list = shopping_list + i + ' шт' + '\n'
                else:
                    shopping_list = shopping_list + i + '\n'
            update.message.reply_text(shopping_list)
            creating = False
            save_list(update, context, shopping_list)
    elif save:
        if update.message.text == 'Да':
            update.message.reply_text('Список успешно сохранён')
            save = False
        elif update.message.text == 'Нет':
            shopping_list = ''
            list_prod = []
            save = False
            update.message.reply_text('Список удален')

    elif writing_adrs:
        address = update.message.text
        update.message.reply_text("Ты успешно установил адрес")
        done_address = True
        writing_adrs = False

    elif check:
        if update.message.text == 'Добавить элемент':
            add_to_list = True
            update.message.reply_text('Укажи продукты, которые ты хочешь добавить\nКогда закончишь, напиши СТОП')
        if add_to_list:
            if update.message.text != 'СТОП' and update.message.text != 'стоп' and update.message.text != 'Стоп':
                list_prod.append(update.message.text)
            else:
                # list_prod.pop(list_prod.index(list_prod[-1]))
                update.message.reply_text('Вот твой изменённый список:')
                for i in sorted(list_prod):
                    if i == 'Добавить элемент':
                        list_prod.remove(i)
                    else:
                        if not i[-1].isalpha():
                            shopping_list = shopping_list + i + ' шт' + '\n'
                        else:
                            shopping_list = shopping_list + i + '\n'
                update.message.reply_text(shopping_list)
                check = False

        elif update.message.text == 'Удалить элемент':
            del_from_list = True
            update.message.reply_text('Укажи продукты, которые ты хочешь удалить\nКогда закончишь, напиши СТОП')
        if del_from_list:
            if update.message.text != 'СТОП' and update.message.text != 'стоп':
                add_prod.append(update.message.text)
            else:
                for element in add_prod:
                    if element in list_prod:
                        a = list_prod.index(element)
                        del list_prod[a]
                update.message.reply_text('Вот твой изменённый список:')
                update.message.reply_text('\n'.join(list_prod))
                check = False

        elif update.message.text == 'Удалить список':
            list_prod = []
            update.message.reply_text('Список успешно удалён')
            check = False

    elif route:
        coordinates_shop = update.message.text
        route = False

    elif to_map:
        coordinates_home = coordinates(update, context, address)
        if not route:
            coordinates_shop = coordinates(update, context, coordinates_shop)
            print(coordinates_shop)
            geocoder_request = 'https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&' \
                               f'geocode={coordinates_shop}&ll={coordinates_home}&format=json'
            result = coordinates(update, context, geocoder_request)
            map_shop = 'https://static-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&' \
                       f'll={result}&spn=0.005457,0.00319&l=map&pt={result},pm2pn2m~{coordinates_home},pm2pn2m'
            map_shop = requests.get(map_shop)
            context.bot.send_photo(map_shop)
            route = True
    else:
        update.message.reply_text('Прости, я тебя не понял. Воспользуся одной из команд /start')


def edit_list(update, context):
    update.message.reply_text('Что ты хочешь сделать со списком')
    choose(update, context)


def choose(update, context):
    global check
    update.message.reply_text('Выбери один из вариантов', reply_markup=markup_list)
    check = True


def save_list(update, context, saving_list):  # сохранение списка в бд
    global save
    update.message.reply_text("Ты хочешь сохранить список?", reply_markup=markup_1)
    save = True


def coordinates(update, context, name):
    name = name.split()
    name = '+'.join(name)
    geocoder_request = 'https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&' \
                       f'geocode={name}&format=json'
    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = str(toponym["Point"]["pos"])
        print(','.join(toponym_coodrinates.split()))
        return ','.join(toponym_coodrinates.split())


def find_shop(update, context):
    global done_address, to_map
    if done_address:
        update.message.reply_text('Укажите название магазина')
        to_map = True
    else:
        update.message.reply_text('Вы не указали адрес, рядом с которым мы удем искать магазин\n'
                                  'Воспользуйтесь командой /setaddress')


def get_list(update, context):
    global shopping_list, list_prod
    update.message.reply_text('Вот твой список:')
    for i in list_prod:
        if not i[-1].isalpha():
            shopping_list = shopping_list + i + ' шт' + '\n'
        else:
            shopping_list = shopping_list + i + '\n'
    update.message.reply_text(shopping_list)


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("setaddress", write_address))
    dp.add_handler(CommandHandler("makealist", create_list))
    dp.add_handler(CommandHandler("editlist", edit_list))
    dp.add_handler(CommandHandler("mylist", get_list))
    dp.add_handler(CommandHandler('findshop', find_shop))
    dp.add_handler(MessageHandler(Filters.text, reaction))
    dp.add_handler(CommandHandler("help", help_me))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
