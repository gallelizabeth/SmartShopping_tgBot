import logging
import math

import requests
import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

from data import db_session
from data.users import User

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5182243678:AAH315moUblzcJYSXYfzS57jIZxNUeVqDMU'

markup = ReplyKeyboardRemove()

done_address = False
creating = False
saving = False
writing_adrs = False
save = False
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
    """
    Запуск бота
    """
    reg(update, context)
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


def reg(update, context):
    """
    Регистрация
    """
    user = User()
    user.name = update.message.chat.id
    user.address = ''
    user.shopping_list = ''
    user.coordinates_shop = ''
    user.list_prod = ''
    if db_sess.query(User).filter(User.name == update.message.chat.id).count() == 0:
        db_sess.add(user)

    db_sess.commit()


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
    user = db_sess.query(User).filter(User.name == update.message.chat.id).first()

    update.message.reply_text('Введи название продукта и его количество через пробел')
    update.message.reply_text('Когда закончишь, напиши СТОП')
    user.list_prod = ''
    db_sess.commit()
    creating = True


def reaction(update, context):
    global creating, saving, route
    global route_done
    global writing_adrs, done_address, save, check, add_to_list, del_from_list, del_list, to_map
    user = db_sess.query(User).filter(User.name == update.message.chat.id).first()
    if creating:
        if update.message.text == 'СТОП' or update.message.text == 'стоп' or update.message.text == 'Стоп':
            user.list_prod = user.list_prod[:-1]
            get_list(update, context)
            creating = False
            save_list(update, context, user.shopping_list)
        else:
            user.list_prod = user.list_prod + update.message.text + ','

    elif save:
        if update.message.text == 'Да':
            db_sess.commit()
            update.message.reply_text('Список успешно сохранён', reply_markup=markup)
            save = False
        elif update.message.text == 'Нет':
            user.shopping_list = ''
            user.list_prod = ''
            db_sess.commit()
            save = False
            update.message.reply_text('Список удален', reply_markup=markup)

    elif writing_adrs:
        print(user)
        print(update.message.text)
        user.address = update.message.text
        db_sess.commit()
        update.message.reply_text("Ты успешно установил адрес")
        done_address = True
        writing_adrs = False

    elif check:
        function_edit_list(update, context)

    elif add_to_list:
        if update.message.text != 'СТОП' and update.message.text != 'стоп' and update.message.text != 'Стоп':
            user.list_prod = user.list_prod + ',' + update.message.text + ','
        else:
            user.list_prod = user.list_prod[:-1]
            user.shopping_list = ''
            db_sess.commit()
            get_list(update, context)
            add_to_list = False
            check = False

    elif del_from_list:
        list_user_prod = str(user.list_prod).split(',')
        if update.message.text != 'СТОП' and update.message.text != 'стоп'\
                and update.message.text != 'Стоп':
            for item in list_user_prod:
                if update.message.text in item:
                    list_user_prod.remove(item)
                    user.list_prod = ','.join(list_user_prod)
            db_sess.commit()
        else:
            get_list(update, context)
            del_from_list = False
            check = False

    elif route:
        user.coordinates_shop = update.message.text
        route = False
        make_map(update, context, user.coordinates_shop)
    else:
        if update.message.text != user.address:
            update.message.reply_text('Прости, я тебя не понял. Воспользуйся одной из команд /start',
                                      reply_markup=markup)


def make_map(update, context, shop):
    user = db_sess.query(User).filter(User.name == update.message.chat.id).first()
    global to_map
    long_h, lat_h = coordinates(update, context, user.address)
    shop = '+'.join((shop.split()))
    geocoder_request = 'https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&' \
                       f'geocode=Москва+{shop}&format=json'
    result = requests.get(geocoder_request)
    if result:
        json_response = result.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = str(toponym["Point"]["pos"])
        long_s, lat_s = toponym_coodrinates.split()
        result, spn = lonlat_distance(long_s, lat_s, long_h, lat_h)
        middle_long = (float(long_s) + float(long_h)) / 2
        middle_lat = (float(lat_s) + float(lat_h)) / 2
        map_shop = 'https://static-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&' \
                   f'll={middle_long},{middle_lat}&spn={spn}&l=map&pt={long_s},{lat_s},' \
                   f'pm2ntm~{long_h},{lat_h},pm2pnm'
        print(map_shop)
        map_shop = requests.get(map_shop)
        print(map_shop)
        with open('map.png', 'wb') as f:
            f = f.write(map_shop.content)
        context.bot.send_photo(chat_id=user.name, photo=map_shop.content,
                               caption=f'Расстояние = {result} '
                                       f'метров\n'
                                       'Розовым цветом обозначен магазин, а синим - отправная точка')
    else:
        update.message.reply_text('Вышла ошибка! Проверь написание адресов и попробуй ещё раз')
    to_map = False


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
    elif distance <= 900:
        spn = '0.009,0.006'
    else:
        spn = '0.1,0.1'

    return round(distance, 2), spn


def edit_list(update, context):
    global check
    update.message.reply_text('Что ты хочешь сделать со списком')
    check = True
    choose(update, context)


def function_edit_list(update, context):
    user = db_sess.query(User).filter(User.name == update.message.chat.id).first()
    global add_to_list, check, del_from_list, list_prod
    if update.message.text == 'Добавить элемент':
        add_to_list = True
        check = False
        update.message.reply_text('Укажи продукты, которые ты хочешь добавить\n'
                                  'Когда закончишь, напиши СТОП', reply_markup=markup)
    elif update.message.text == 'Удалить элемент':
        del_from_list = True
        check = False
        update.message.reply_text('Укажи продукты, которые ты хочешь удалить\n'
                                  'Когда закончишь, напиши СТОП', reply_markup=markup)
    elif update.message.text == 'Удалить список':
        user.list_prod = ''
        db_sess.commit()
        update.message.reply_text('Список успешно удалён', reply_markup=markup)
        check = False


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
    """
    Вывод списка
    """
    user = db_sess.query(User).filter(User.name == update.message.chat.id).first()
    if len(user.list_prod) != 0:
        update.message.reply_text('Вот твой список:')
        user.shopping_list = ''
        res_list = str(user.list_prod).split(',')
        for i in res_list:
            if not i[-1].isalpha() or not i[-2].isalpha():
                user.shopping_list = user.shopping_list + i + ' шт' + '\n'
            else:
                user.shopping_list = user.shopping_list + i + '\n'
        update.message.reply_text(user.shopping_list)
    else:
        update.message.reply_text('Список пуст')


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
    db_session.global_init("db/smart_shopping_list.db")
    db_sess = db_session.create_session()
    main()
