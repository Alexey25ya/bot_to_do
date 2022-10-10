
import telebot
from datetime import datetime as dt
import logging
import operations as o
from operations import read_csv
from config import TOKEN
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)
import stickers as st
import config

bot = telebot.TeleBot(config.TOKEN)
# Включим ведение журнала
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Определяем константы этапов разговора

START,MAIN_MENU, SUB_MENU, MENU, EDIT, ADD,NAME,SURNAME,STATUS,DELETE, VIEW, SEARCH, SEARCH_MENU= range(13)


# функция обратного вызова точки входа в разговор

def start(update, context):
    reply_keyboard = [['🎬START','🚪EXIT']]
    markup_key = ReplyKeyboardMarkup(
        reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    context.bot.send_sticker(update.message.chat.id, st.welcome)
    context.bot.send_message(update.effective_chat.id,
                     f'Добро пожаловать в список дел, {update.effective_user.first_name}!\n'
        'Для начала работы со списком нажмите кнопку 🎬START\n'
        'Для выхода нажмите кнопку 🚪EXIT', reply_markup=markup_key)

    return MAIN_MENU


def main_menu(update, context):
    user = update.message.from_user
    logger.info("Выбор операции: %s: %s", user.first_name, update.message.text)
    choice = update.message.text
    if choice == '🎬START':
        return sub_menu(update, context)
    if choice == '🚪EXIT':        
        return cancel(update, context)

def sub_menu(update, context):
    reply_keyboard = [['👀 VIEW', '📝 ADD','🔎 SEARCH', '❌ DELETE', '✍ EDIT', '🚪 EXIT']]
    markup_key = ReplyKeyboardMarkup(
        reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    context.bot.send_sticker(update.message.chat.id, st.hello)
    update.message.reply_text('Выберете действие со списком дел ', reply_markup=markup_key)
    return MENU

def menu(update, context):
    user = update.message.from_user
    logger.info("Выбор операции: %s: %s", user.first_name, update.message.text)
    choice = update.message.text
    if choice == '👀 VIEW':
        return view(update, context)
    if choice == '📝 ADD':
        update.message.reply_text("Введите имя исполнителя")
        return NAME
    if choice == '🔎 SEARCH':
        context.bot.send_sticker(update.message.chat.id, st.listen)
        context.bot.send_message(update.effective_chat.id,
                     f'Что бы вы хотели найти,{update.effective_user.first_name}: ')
        return SEARCH
    if choice == '❌ DELETE':
        update.message.reply_text("Найти задачу для удаления: ")
        return DELETE
    if choice == '✍ EDIT':
        update.message.reply_text("Найти задачу для редактирования: ")
        return EDIT    
    if choice == '🚪 EXIT':
        return cancel(update, context)


def view(update, context):
    user = update.message.from_user
    logger.info("Контакт %s: %s", user.first_name, update.message.text)
    context.bot.send_sticker(update.message.chat.id, st.view_sticker)
    context.bot.send_message(update.effective_chat.id,
                     f'А вот и список задач, {update.effective_user.first_name} ')
    tasks = read_csv()
    tasks_string = o.view_tasks(tasks)
    update.message.reply_text(tasks_string)
    return sub_menu(update, context)



def name(update, context):
    user = update.message.from_user
    logger.info("Task %s: %s", user.first_name, update.message.text)
    name = update.message.text
    context.user_data['name'] = name
    update.message.reply_text("Введите фамилию исполнителя")
    return SURNAME

def surname(update, context):
    user = update.message.from_user
    logger.info("Task %s: %s", user.first_name, update.message.text)
    surname = update.message.text
    context.user_data['surname'] = surname
    update.message.reply_text("Введите статус задания:\n <в поцессе выполнения>\n <выполнено>")
    return STATUS

def status(update, context):
    user = update.message.from_user
    logger.info("Task %s: %s", user.first_name, update.message.text)
    status= update.message.text
    context.user_data['status'] = status
    update.message.reply_text("Введите задачу")
    return ADD

def add(update, context):
    tasks = read_csv()
    task = {}
    user = update.message.from_user
    logger.info("Task %s: %s", user.first_name, update.message.text)
    add_task = update.message.text
    name = context.user_data.get('name')
    surname = context.user_data.get('surname')
    status = context.user_data.get('status')
    task['Имя'] = name
    task['Фамилия'] = surname
    task['Статус выполнения'] = status
    task['Задача'] = add_task
    tasks.append(task)
    o.write_csv(tasks)
    context.bot.send_sticker(update.message.chat.id, st.complete)
    context.bot.send_message(update.effective_chat.id,
                    f'{update.effective_user.first_name}, задача {task} успешно добавлена!:')
    return sub_menu(update, context)


def search(update, context):
    user = update.message.from_user
    logger.info("Выбор поиска: %s: %s", user.first_name, update.message.text)
    searchstring = update.message.text
    tasks = read_csv()
    searched_tasks = o.search_task(searchstring, tasks)
    if searched_tasks==[]:
            context.bot.send_message(update.effective_chat.id,
                    f' {update.effective_user.first_name}, по вашему запросу "{searchstring}" ничего не найдено:')
    else:                
        context.bot.send_message(update.effective_chat.id,
                        f' {update.effective_user.first_name}, по вашему запросу "{searchstring}" найдено:')
        tasks_string = o.view_tasks(searched_tasks)
        update.message.reply_text(tasks_string)

    return sub_menu(update, context)

    


def delete(update, context):
    user = update.message.from_user
    logger.info("Выбор удаления: %s: %s", user.first_name, update.message.text)
    searchstring = update.message.text
    searched_task=o.delete_task(searchstring)
    context.bot.send_sticker(update.message.chat.id, st.complete)
    update.message.reply_text(f'{searched_task}')
    return sub_menu(update, context)

    
def edit(update, context):
    user = update.message.from_user
    logger.info("Выбор редактирования: %s: %s", user.first_name, update.message.text)
    searchstring = update.message.text
    searched_task=o.delete_task(searchstring)
    context.bot.send_sticker(update.message.chat.id, st.complete)
    update.message.reply_text(f'{searched_task}')
    update.message.reply_text("Введите имя исполнителя" )
    return NAME



def cancel(update, context):
    # определяем пользователя
    user = update.message.from_user
    # Пишем в журнал о том, что пользователь не разговорчивый
    logger.info("Пользователь %s отменил разговор.", user.first_name)
    # Отвечаем на отказ поговорить
    context.bot.send_sticker(update.message.chat.id, st.goodbye)
    context.bot.send_message(update.effective_chat.id,
                     f'До новых встреч, {update.effective_user.first_name}. 👋'
        'Для вызова меню списка дел нажмите /start')
    context.bot.send_sticker(update.message.chat.id, st.relax)
    return ConversationHandler.END


if __name__ == '__main__':
    # Создаем Updater и передаем ему токен вашего бота.
    updater = Updater(TOKEN)
    # получаем диспетчера для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Определяем обработчик разговоров `ConversationHandler`
    # с состояниями GENDER, PHOTO, LOCATION и BIO
    game_conversation_handler = ConversationHandler(  # здесь строится логика разговора
        # точка входа в разговор
        entry_points=[CommandHandler('start', start)],
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            VIEW: [MessageHandler(Filters.text, view)],
            START: [CommandHandler('start', start)],
            SUB_MENU: [MessageHandler(Filters.text, sub_menu)],
            ADD: [MessageHandler(Filters.text, add)],
            NAME: [MessageHandler(Filters.text, name)],
            SURNAME: [MessageHandler(Filters.text, surname)],
            STATUS: [MessageHandler(Filters.text, status)],
            DELETE: [MessageHandler(Filters.text, delete)],
            SEARCH: [MessageHandler(Filters.text, search)],
            MENU: [MessageHandler(Filters.text, menu)],
            MAIN_MENU: [MessageHandler(Filters.text,main_menu)],
            EDIT: [MessageHandler(Filters.text, edit)],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Добавляем обработчик разговоров `conv_handler`
    dispatcher.add_handler(game_conversation_handler)

    # Запуск 
    print('SERVER_STARTED')
    updater.start_polling()
    updater.idle()