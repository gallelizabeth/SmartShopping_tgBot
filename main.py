import logging
import math

import requests
import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5349979559:AAHcXnyvYcT_ETNfqlJiJNC3uDjicwmU3mM'

markup = ReplyKeyboardRemove()

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
route = False
to_map = False
route_done = False

bot = telegram.Bot(TOKEN)

# keyboard
save_items = [['Да', 'Нет']]
check_list = [['Добавить элемент', 'Удалить элемент', 'Удалить список']]
markup_1 = ReplyKeyboardMarkup(save_items, one_time_keyboard=True)
markup_list = ReplyKeyboardMarkup(check_list, one_time_keyboard=True)


def start(update, context):
    update.message.reply_text("Привет! Я помогу тебе составить список покупок и найти нужный магазин",
                              reply_markup=markup)
    update.message.reply_text("Рекомендую задать свой адрес командой /setaddress для более качественного"
                              " пользования\n"
                              "Также ты сможешь управлять мной, используя эти команды:\n"
                              "/makealist – собрать список\n"
                              "/editlist – редактировать список\n"
                              "/mylist – посмотреть список\n"
                              "/findshop – посмотреть расположение магазина относительно"
                              "заданного адреса и узнать расстояние между ними\n"
                              "нажмите /help , если тебе понадобится помощь\n"
                              "БОТ ОСУЩЕСТВЛЯЕТ РАБОТУ ТОЛЬКО В ПРЕДЕЛАХ МОСКВЫ")


def write_address(update, context):
    global writing_adrs
    update.message.reply_text("Укажи адрес, от которого будет отсчитыться расстояние до магазина")
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
    global shopping_list, creating, saving, all_lists, list_prod, route, address, coordinates_shop, route_done
    global writing_adrs, done_address, add_prod, save, check, add_to_list, del_from_list, del_list, to_map
    if creating:
        list_prod.append(update.message.text)
        if update.message.text == 'СТОП' or update.message.text == 'стоп' or update.message.text == 'Стоп':
            list_prod.pop(list_prod.index(list_prod[-1]))
            get_list(update, context)
            creating = False
            save_list(update, context, shopping_list)
    elif save:
        if update.message.text == 'Да':
            update.message.reply_text('Список успешно сохранён', reply_markup=markup)
            save = False
        elif update.message.text == 'Нет':
            shopping_list = ''
            list_prod = []
            save = False
            update.message.reply_text('Список удален', reply_markup=markup)

    elif writing_adrs:
        address = update.message.text
        update.message.reply_text("Ты успешно установил адрес")
        done_address = True
        writing_adrs = False

    elif check:
        if update.message.text == 'Добавить элемент':
            add_to_list = True
            check = False
            update.message.reply_text('Укажи продукты, которые ты хочешь добавить\nКогда закончишь, напиши СТОП')
        elif update.message.text == 'Удалить элемент':
            del_from_list = True
            check = False
            update.message.reply_text('Укажи продукты, которые ты хочешь удалить\nКогда закончишь, напиши СТОП')
        elif update.message.text == 'Удалить список':
            list_prod = []
            update.message.reply_text('Список успешно удалён')
            check = False

    elif add_to_list:
        if update.message.text != 'СТОП' and update.message.text != 'стоп' and update.message.text != 'Стоп':
            list_prod.append(update.message.text)
        else:
            shopping_list = ''
            for i in sorted(list_prod):
                if i == 'Добавить элемент':
                    list_prod.remove(i)
                else:
                    get_list(update, context)
            add_to_list = False
            check = False

    elif del_from_list:
        if update.message.text != 'СТОП' and update.message.text != 'стоп'\
                and update.message.text != 'Стоп':
            for item in list_prod:
                if update.message.text in item:
                    list_prod.remove(item)
        else:
            get_list(update, context)
            del_from_list = False
            check = False

    elif route:
        coordinates_shop = update.message.text
        route = False
        to_map = True
        route_done = True

    elif to_map:
        long_h, lat_h = coordinates(update, context, address)
        if route_done:
            coordinates_shop = '+'.join((coordinates_shop.split()))
            geocoder_request = 'https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&' \
                               f'geocode=Москва+{coordinates_shop}&format=json'
            result = requests.get(geocoder_request)
            if result:
                json_response = result.json()
                toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                toponym_coodrinates = str(toponym["Point"]["pos"])
                long_s, lat_s = toponym_coodrinates.split()
                result, spn = lonlat_distance(long_s, lat_s, long_h, lat_h)
                map_shop = 'https://static-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&' \
                           f'll={long_s},{lat_s}&spn={spn}&l=map&pt={long_s},{lat_s},' \
                           f'pm2pnm~{long_h},{lat_h},pm2pnm'
                map_shop = requests.get(map_shop)
                context.bot.send_photo(chat_id=update.message.chat.id, photo=map_shop.content,
                                       caption=f'Расстояние = {result} '
                                               f'метров')
            else:
                update.message.reply_text('Вышла ошибка! Проверь написание адресов и попробуй ещё раз')
            to_map = False
    else:
        if update.message.text != address:
            update.message.reply_text('Прости, я тебя не понял. Воспользуйся одной из команд /start',
                                      reply_markup=markup)


def lonlat_distance(a_lon, a_lat, b_lon, b_lat):

    degree_to_meters_factor = 111 * 1000
    a_lon = float(a_lon)
    a_lat = float(a_lat)
    b_lon = float(b_lon)
    b_lat = float(b_lat)

    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    distance = math.sqrt(dx * dx + dy * dy)

    if distance <= 300:
        spn = '0.006,0.004'
    elif distance <= 800:
        spn = '0.009,0.006'
    else:
        spn = '0.009,0.009'

    return round(distance, 2), spn


def edit_list(update, context):
    global check
    update.message.reply_text('Что ты хочешь сделать со списком')
    check = True
    choose(update, context)


def choose(update, context):
    global check
    update.message.reply_text('Выбери один из вариантов', reply_markup=markup_list)


def save_list(update, context, saving_list):  # сохранение списка в бд
    global save
    update.message.reply_text("Ты хочешь сохранить список?", reply_markup=markup_1)
    save = True


def coordinates(update, context, name):
    name = name.split()
    name = '+'.join(name)
    geocoder_request = 'https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&' \
                       f'geocode=Москва+{name}&format=json'
    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = str(toponym["Point"]["pos"])
        return toponym_coodrinates.split()


def find_shop(update, context):
    global done_address, to_map, route
    if done_address:
        update.message.reply_text('Укажи адрес магазина')
        route = True
    else:
        update.message.reply_text('Ты не указал(-а) адрес, от которого мы будем отсчитывать расстояние\n'
                                  'Воспользуйтесь командой /setaddress')


def get_list(update, context):
    global shopping_list, list_prod
    update.message.reply_text('Вот твой список:')
    shopping_list = ''
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
