import logging
import math
import os.path

import requests
import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, message
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from data import db_session
from data.user import User
import telebot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5182243678:AAH315moUblzcJYSXYfzS57jIZxNUeVqDMU'

markup = ReplyKeyboardRemove()

add_prod = []
current_teleg_id = ''
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


def true_list(lit):
    t = []
    for el in lit:
        el = el.split(' ')
        if not el[-1].isdigit():
            el.extend('1')
        t.append(' '.join(el))
    return t


def start(update, context):
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
    global current_teleg_id
    db_sess = db_session.create_session()
    current_teleg_id = update.message.chat.id
    c = db_sess.query(User).filter(User.teleg_id == current_teleg_id).first()
    if not c:
        user = User()
        user.teleg_id = current_teleg_id
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
    update.message.reply_text('Введи название продукта и его количество через пробел\nКогда закончишь, напиши СТОП')
    creating = True


def reaction(update, context):
    global shopping_list, creating, saving, all_lists, list_prod, route, address, coordinates_shop, route_done
    global writing_adrs, done_address, add_prod, save, check, add_to_list, del_from_list, del_list, to_map, \
        current_teleg_id
    reg(update, context)
    if creating:
        list_prod.append(update.message.text)
        if update.message.text == 'СТОП' or update.message.text == 'стоп' or update.message.text == 'Стоп':
            list_prod.pop(list_prod.index(list_prod[-1]))
            update.message.reply_text('Вот твой список:')
            print(list_prod)
            update.message.reply_text('\n'.join(list_prod))
            creating = False
            save_list(update, context)
    elif save:
        if update.message.text == 'Да':
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.teleg_id == current_teleg_id).first()
            true_list_prod = true_list(list_prod)
            user.spisok = '\n'.join(true_list_prod)
            db_sess.commit()
            db_sess.close()
            update.message.reply_text('Список успешно сохранён', reply_markup=markup)
            save = False
            list_prod.clear()
        elif update.message.text == 'Нет':
            shopping_list = ''
            list_prod.clear()
            save = False
            update.message.reply_text('Список удален', reply_markup=markup)

    elif writing_adrs:
        address = update.message.text
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.teleg_id == current_teleg_id).first()
        user.address = address
        db_sess.commit()
        db_sess.close()
        update.message.reply_text("Ты успешно установил адрес")
        done_address = True
        writing_adrs = False

    elif check:
        if update.message.text == 'Добавить элемент':
            add_to_list = True
            update.message.reply_text('Укажи продукты и количество через пробел, которые '
                                      'ты хочешь добавить\nКогда закончишь, напиши СТОП')
        if add_to_list:
            if update.message.text != 'СТОП' and update.message.text != 'стоп' and update.message.text != 'Стоп':
                add_prod.append(update.message.text)
            else:
                db_sess = db_session.create_session()
                user = db_sess.query(User).filter(User.teleg_id == current_teleg_id).first()
                spisok = user.spisok
                spisik_kopy = spisok.split('\n')
                list_ = spisok.split('\n')
                add_prod.remove('Добавить элемент')
                print(add_prod)
                for element in add_prod:
                    for i in spisik_kopy:
                        list_kopy = ' '.join(list_)
                        if element in spisok:
                            if element in i:
                                if not i.isalpha():
                                    n = i.split(' ')
                                    int_n = int(n[len(n) - 1])
                                    if not element.isalpha():
                                        int_n += int(element[len(element) - 1])
                                        n[len(n) - 1] = str(int_n)
                                        list_.append(' '.join(n))
                                    else:
                                        int_n += 1
                                        list_.remove(i)
                                        n[len(n) - 1] = str(int_n)
                                        list_.append(' '.join(n))
                                else:
                                    spisik_kopy = str(i) + ' 2'
                                    list_.append(spisik_kopy)
                        else:
                            if element not in list_kopy:
                                list_.append(element)
                print(spisok)
                true_list_prod = true_list(list_)
                user.spisok = '\n'.join(true_list_prod)
                db_sess.commit()
                db_sess.close()
                add_prod.clear()
                update.message.reply_text('Твой список успешно изменён')
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
        db_sess = db_session.create_session()
        db_sess.coordinates_shop = update.message.text
        route = False
        make_map(update, context, db_sess.coordinates_shop)
    else:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.teleg_id == current_teleg_id).first()
        adres = user.address
        if update.message.text != adres:
            update.message.reply_text('Прости, я тебя не понял. Воспользуйся одной из команд /start',
                                      reply_markup=markup)


def make_map(update, context, shop):
    db_sess = db_session.create_session()
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
    update.message.reply_text('Что ты хочешь сделать со списком')
    choose(update, context)


def choose(update, context):
    global check
    update.message.reply_text('Выбери один из вариантов', reply_markup=markup_list)
    check = True


def save_list(update, context):  # сохранение списка в бд
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
    reg(update, context)
    update.message.reply_text('Вот твой список:')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.teleg_id == current_teleg_id).first()
    update.message.reply_text(user.spisok)


def main():
    db_session.global_init(os.path.join("db/shopping_bot.db"))
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
