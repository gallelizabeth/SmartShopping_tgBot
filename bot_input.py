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
    update.message.reply_text('Составляем список..')


def edit_list(update, context):
    pass


def find_shop(update, context):
    if done_address:
        update.message.reply_text('Поиск..')
    else:
        update.message.reply_text('Упс! Похоже, ты не указал адрес')


def edit_address(update, context):
    if done_address:
        update.message.reply_text('Похоже, ты хочешь поменять адрес')
        write_address(update, context)
    else:
        update.message.reply_text('Упс! Похоже, ты не указал адрес')


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
