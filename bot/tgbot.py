import telebot
from telebot import types
import requests

url = "http://fastapi:8000"
bot = telebot.TeleBot("TOKEN")

# Глобальные переменные для хранения информации о текущем состоянии
current_vacancy_id = 1
total_vacancies = 0
current_criteria = ""
stop_flag = False


@bot.message_handler(commands=["start"])
def start_bot(message):
    first_message = f"<b>{message.from_user.first_name}</b>, привет!\nХочешь, чтобы я помог тебе найти работу?"
    markup = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    button_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    markup.add(button_yes, button_no)
    bot.send_message(message.chat.id, first_message, parse_mode='html', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def response(call):
    global current_vacancy_id, stop_flag

    if call.message:
        if call.data == "yes":
            second_message = "Введи название интересующей тебя должности,\n и посмотрим, что я смогу для тебя найти."
            bot.send_message(call.message.chat.id, second_message)
        elif call.data == "no":
            second_message = "Тогда я ничем не смогу тебе помочь,\n так как больше ничего не умею."
            bot.send_message(call.message.chat.id, second_message)
        elif call.data == 'next':
            bot.answer_callback_query(call.id)
            send_next_vacancy(call.message.chat.id)
        elif call.data == 'stop':
            bot.answer_callback_query(call.id, text="Поиск остановлен.")
            stop_flag = True
        else:
            bot.answer_callback_query(call.id)


@bot.message_handler(content_types=["text"])
def get_vacancy(message):
    global current_vacancy_id, total_vacancies, current_criteria, stop_flag

    criteria = message.text
    bot.send_message(message.chat.id, f"Начал поиск по запросу: {criteria}.\nПодожди, это может занять время.")

    stop_flag = False

    try:
        # Отправляем запрос на сервер для парсинга
        response = requests.post(url=f"{url}/pars/vacancies", json={"criteria": criteria})
        response.raise_for_status()
    except requests.RequestException as e:
        bot.send_message(message.chat.id, f"Ошибка при парсинге вакансий: {e}")
        return

    try:
        # Получаем количество строк в таблице
        response = requests.get(url=f"{url}/get_count", params={"table_name": criteria})
        response.raise_for_status()
        data = response.json()

        total_vacancies = data["count"]
        current_vacancy_id = 1  # Сбрасываем id текущей вакансии
        current_criteria = criteria

        if total_vacancies > 0:
            bot.send_message(message.chat.id, f"Найдено {total_vacancies} вакансий.")
            send_next_vacancy(message.chat.id)
        else:
            bot.send_message(message.chat.id, "Вакансии не найдены.")
    except requests.RequestException as e:
        bot.send_message(message.chat.id, f"Ошибка получения данных из базы данных: {e}")
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка: некорректный JSON в ответе сервера")


def send_next_vacancy(chat_id):
    global current_vacancy_id, total_vacancies, current_criteria, stop_flag

    while current_vacancy_id <= total_vacancies and not stop_flag:
        try:
            # Получаем следующую вакансию по id
            response = requests.get(url=f"{url}/get_vacancy", params={"id": current_vacancy_id, "table_name": current_criteria})
            response.raise_for_status()
            vacancy = response.json().get("vacancy")

            if vacancy:
                if all(not value for value in vacancy.values()):
                    current_vacancy_id += 1
                    continue  # Если все поля вакансии пустые, переходим к следующей
                vacancy_message = f"Вакансия: {vacancy['title']}\n" \
                                  f"Зарплата: {vacancy['salary']}\n" \
                                  f"Опыт: {vacancy['experience']}\n" \
                                  f"Компания: {vacancy['company']}\n" \
                                  f"Теги: {(vacancy['tags']).replace('&', '  //  ')}"

                # Создаем кнопки для ссылки на вакансию, "Дальше" и "Стоп"
                markup = types.InlineKeyboardMarkup()
                url_button = types.InlineKeyboardButton(text='Перейти к вакансии', url=vacancy['url'])
                button_next = types.InlineKeyboardButton(text='Дальше', callback_data='next')
                button_stop = types.InlineKeyboardButton(text='Стоп', callback_data='stop')
                markup.add(url_button)
                markup.add(button_next, button_stop)

                # Отправляем сообщение с вакансией
                bot.send_message(chat_id, vacancy_message, reply_markup=markup, parse_mode='HTML')

                current_vacancy_id += 1  # Увеличиваем id только после отправки текущей вакансии
                break
            else:
                current_vacancy_id += 1  # Если вакансия не найдена, переходим к следующей
        except requests.RequestException as e:
            bot.send_message(chat_id, f"Ошибка получения данных из базы данных: {e}")
            break

        except ValueError:
            bot.send_message(chat_id, "Ошибка: некорректный JSON в ответе сервера")
            break
    else:
        if not stop_flag:
            bot.send_message(chat_id, "Больше вакансий нет.")

bot.infinity_polling()