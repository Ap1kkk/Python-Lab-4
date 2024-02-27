import random
import telebot
import requests
from telebot import types


TOKEN = '7032564105:AAG7YOPZkX3VlpcV3zQToN_NAGH8PGbMQck'
API_KEY = 'AIzaSyCQk5h5aP6HaOFXVWMSe30qX6dozktJVOE'
CX = 'd362dd2850b8748ba'

bot = telebot.TeleBot(TOKEN)

user_images = {}


@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}! Я бот для поиска изображений. "
                                      f"Используй команду /search <твой запрос>, чтобы найти картинки.")


def delete_messages(chat_id, messages):
    for message in messages:
        try:
            bot.delete_message(chat_id=chat_id, message_id=message)
        except Exception as e:
            print(e)


def send_photo(chat_id, photo):
    try:
        bot.send_photo(chat_id, photo)
    except Exception as e:
        print(e)


@bot.message_handler(commands=['search'])
def handle_search(message):
    search_query = ' '.join(message.text.split()[1:])

    if not search_query:
        bot.send_message(message.chat.id, "Пожалуйста, укажи запрос после команды /search.")
        return

    loading_message = bot.send_message(message.chat.id, "Идет поиск изображений...")

    images = search_images(search_query)

    delete_messages(message.chat.id, [loading_message.message_id])

    if images:
        user_images[message.from_user.id] = images

        for i, img_url in enumerate(images[:3], start=1):
            send_photo(message.chat.id, img_url)

        keyboard = types.ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True)
        buttons = [types.KeyboardButton(str(i)) for i in range(1, 4)]
        keyboard.add(*buttons)

        bot.send_message(message.chat.id, "Выбери картинку (1, 2, 3)", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Картинки по запросу не найдены.")


@bot.message_handler(func=lambda message: message.text.isdigit() and int(message.text) in [1, 2, 3])
def handle_choice(message):
    user_id = message.from_user.id

    print(f"handle choise chat id:{message.chat.id} message id:{message.message_id} for user id:{user_id}")

    delete_messages(message.chat.id, [message.message_id - 1, message.message_id - 2,
                                      message.message_id - 3, message.message_id - 4])

    choice = int(message.text)
    if user_id in user_images:
        chosen_image = user_images[user_id][choice - 1]
        bot.send_message(message.chat.id, f"Ты выбрал картинку {choice}. Запрос выполнен.")
        send_photo(message.chat.id, chosen_image)

        del user_images[user_id]
    else:
        bot.send_message(message.chat.id, "Что-то пошло не так. Пожалуйста, начни поиск снова.")


def search_images(query):
    search_url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX}&searchType=image'

    try:
        response = requests.get(search_url)
        data = response.json()
        items = data.get('items', [])
        random.shuffle(items)
        return [item['link'] for item in items]
    except Exception as e:
        print(f"Error: {e}")
        return []


if __name__ == "__main__":
    bot.polling(none_stop=True)
