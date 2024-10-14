import sqlite3
import telebot
import geopy
from geopy.distance import geodesic as GD
from telebot import types

con = sqlite3.connect("base.db", check_same_thread=False)
cursor = con.cursor()

bot = telebot.TeleBot('5952962334:AAGwjEpOrWLhR9JuUOGZ9fSekona_bR_VBU')

# 1 экскурсии
# 3 места
# 4 редактор
# 5 маршрут
# 6 диалоговое поле уточняющее хочет ли человек завершить маррут или начать его
right_str = '>'
left_str = '<'
# show_str = 'Посмотреть'
back_str = 'Назад'
select_str = 'Добавить это место в маршрут'
add_all = 'Добавить вcе места'
delete_str = 'Удалить из маршрута'
delete_this_str = 'Удалить все места из маршрута'
delete_all_str = 'Удалить составленный маршрут'
start_str = 'Мой маршрут'
my_str = 'Начать маршрут'
end_way = 'Завершить маршрут'
yes_str = 'Да'
no_str = 'Нет'
route = []


def create_buttons(message: object, desc: object) -> object:
    if desc == 'Stop':
        bot.send_message(message, 'Приветствую на маршруте!',  reply_markup=types.ReplyKeyboardRemove())
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    left = types.KeyboardButton(left_str)
    right = types.KeyboardButton(right_str)
    # show = types.KeyboardButton(show_str)
    back = types.KeyboardButton(back_str)
    select = types.KeyboardButton(select_str)
    delete_way = types.KeyboardButton(delete_str)
    delete_all = types.KeyboardButton(delete_all_str)
    delete_this = types.KeyboardButton(delete_this_str)
    start_way = types.KeyboardButton(start_str)
    my_way = types.KeyboardButton(my_str, request_location=True)
    yes = types.KeyboardButton(yes_str)
    no = types.KeyboardButton(no_str)
    add = types.KeyboardButton(add_all)

    id_user = message.chat.id  # было message.from_user.id
    cursor.execute('select status from user where id_user = ?', [id_user])
    status = cursor.fetchall()
    stat = status[0][0]
    if stat == 1:
        markup.add(start_way)
        # прикрепленные к сообщению кнопки с типами
    '''
    if stat == 2: # больше не используется
        markup.add(left, right, show, back, select, start_way)
    '''
    if stat == 3:
        cursor.execute(
            'SELECT * FROM route WHERE id_user = ? and id_place = (SELECT id_place FROM user where id_user = ?)',
            [id_user, id_user])
        rows = cursor.fetchall()
        if len(rows) == 0:
            sd = select
        else:
            sd = delete_way
        markup.add(left, right, back, sd, start_way, add)
    if stat == 4:
        markup.add(back, delete_all, my_way)
        # прикрепленная к сообщению кнопка удалить из маршрута
    if stat == 5:
        print("пока не делаем")
    if stat == 6 or stat == 7 or stat == 8:
        markup.add(yes, no)
    # 6 вышли спросить после попытки удалить все
    # 7 при выходе из редактора в путь
    # 8 досрочное завершение маршрута

    bot.send_message(message.chat.id, desc, reply_markup=markup)


def create_line_button(message):
    markup = types.InlineKeyboardMarkup()
    id_user = message.from_user.id
    cursor.execute('select status from user where id_user = ?', [id_user])
    status = cursor.fetchall()
    if status[0][0] == 1:
        cursor.execute('select name from excursion')
        type_name = cursor.fetchall()
        keyboard = telebot.types.InlineKeyboardMarkup()
        for tn in type_name:
            button = telebot.types.InlineKeyboardButton(text=tn[0], callback_data=tn[0])
            keyboard.add(button)
        bot.send_message(message.chat.id, 'Типы маршрутов', reply_markup=keyboard)


def insert_user(user_id: int, place_id: int, excursion_id: int, last_area: int, status: int):
    cursor.execute('INSERT INTO user (id_user, id_place, id_excursion, last_area, status ) VALUES (?, ?, ?, ?, ?)',
                   (user_id, place_id, excursion_id, last_area, status))
    con.commit()


def update_user_status(value: int, id_user: int):
    cursor.execute('UPDATE user SET status = ? where id_user = ?', [value, id_user])
    con.commit()


def update_user_id_excursion(value: int, id_user: int):
    cursor.execute('UPDATE user SET id_excursion = ? where id_user = ?', [value, id_user])
    con.commit()


def update_user_id_place(value: int, id_user: int):
    cursor.execute('UPDATE user SET id_place = ? where id_user = ?', [value, id_user])
    con.commit()


def update_user_last_area(value: int, id_user: int):
    cursor.execute('UPDATE user SET last_area = ? where id_user = ?', [value, id_user])
    con.commit()


def insert_route(user_id: int, place_id: int):
    cursor.execute('INSERT INTO route (id_user, id_place, status) VALUES (?, ?, 0)', (user_id, place_id))
    con.commit()


# status
# 0 не посетил
# 1 посетил

def update_route_status(id_user: int):
    cursor.execute('UPDATE route SET status = 1 where id_user = ?', [id_user])
    con.commit()


def delete_route(id_user: int):
    cursor.execute('select id_place from user where id_user = ?', [id_user])
    id_place = cursor.fetchall()
    cursor.execute('DELETE FROM route WHERE id_user = ? and id_place = ?', [id_user, id_place[0][0]])
    con.commit()


@bot.message_handler(commands=['start'])
def start(message):
    id_user = message.from_user.id
    cursor.execute('select status from user where id_user = ?', [id_user])
    rows = cursor.fetchall()
    if len(rows) == 0:
        #bot.send_message(message.chat.id, 'Добро пожаловать, выберите экскурсию которую хотите посмотреть')
        insert_user(user_id=id_user, place_id=None, excursion_id=None, last_area=None, status=1)
    else:
        update_user_status(value=1, id_user=id_user)
    create_buttons(message, "Добро пожаловать ☀️")
    create_line_button(message)


@bot.message_handler(commands=['help'])
def help(message):
    help_text = "- Нажмните /start для начала работы\n- Из списка предложенных мест выберите понравившееся\n- Отправляйтесь в путешествие)"
    bot.send_message(message.chat.id, help_text)


'''
def show_excursions(message: types.Message, id_excursion: int):
    cursor.execute('select name, desc, photo from excursion where id_excursion = ?', [id_excursion])
    excursion = cursor.fetchall()
    img = open(excursion[0][2], 'rb')
    bot.send_photo(message.chat.id, img)
    bot.send_message(message.chat.id, excursion[0][0])
    bot.send_message(message.chat.id, excursion[0][1])
'''


# была переделана
@bot.callback_query_handler(func=lambda call: True)
def excursions_types(call: types.CallbackQuery):
    if call.data[:4] == "Cart":
        places = call.data
        cursor.execute('select longitude, latitude from place where name = ?', [places[4:]])
        place = cursor.fetchall()
        bot.send_location(call.message.chat.id, place[0][1], place[0][0])
        return
    if call.data == "Next":
        cursor.execute('select full_desc from place where id_place = ?', [route[0][1]])
        place = cursor.fetchall()
        texts = str(place[0][0])
        special = texts.find('❗')
        if special != -1:
            bot.answer_callback_query(call.id, texts[special + 1:], show_alert=True)
        if len(route) == 1:
            next_place(call.message, route[0][1], '', -1)
            bot.send_message(call.message.chat.id, "Конец пути! Вернуться в начало /start")
        if len(route) > 1:
            next_place(call.message, route[0][1], '', 1)
    cursor.execute('select name from excursion')
    excursion_type_list = cursor.fetchall()
    flag = 0
    excursion_type = 0
    for t in excursion_type_list:
        if t[0] == call.data:
            flag = 1
            excursion_type = t[0]
            break
    if flag == 1:
        update_user_status(value=3, id_user=call.message.chat.id)
        cursor.execute('select id_excursion from excursion where name = ?', [excursion_type])
        id_excursion_type = cursor.fetchall()
        update_user_id_excursion(value=id_excursion_type[0][0], id_user=call.message.chat.id)
        cursor.execute('select id_place from place where id_excursion = ?', [id_excursion_type[0][0]])
        id_place = cursor.fetchall()

        update_user_id_place(value=id_place[0][0], id_user=call.message.chat.id)
        cursor.execute('select name from place where id_place = ?', [id_place[0][0]])
        place = cursor.fetchall()
        create_buttons(call.message, place[0][0])
        show_places(call.message, id_place[0][0])


def show_places(message: types.Message, id_place: int):
    cursor.execute('select name, desc from place where id_place = ?', [id_place])
    place = cursor.fetchall()
    cursor.execute('select photo from photo where id_place = ?', [id_place])
    place_photo = cursor.fetchall()
    keyboard = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton(text='Местоположение', callback_data="Cart" + place[0][0])
    keyboard.add(button)
    caption = "<a href='" + str(place_photo[0][0]) + "'>&#8203;</a>"
    bot.send_message(message.chat.id, place[0][1] + caption, parse_mode='HTML', reply_markup=keyboard)


def next_place(message: types.Message, id_place: int, capt: str, nexts: int):
    route.remove(route[0])
    cursor.execute('select name, full_desc from place where id_place = ?', [id_place])
    place = cursor.fetchall()
    cursor.execute('select photo from photo where id_place = ?', [id_place])
    place_photo = cursor.fetchall()
    keyboard = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(text='Местоположение', callback_data="Cart" + place[0][0])
    #button2 = telebot.types.InlineKeyboardButton(text='Больше информации', callback_data="Info" + place[0][0])
    keyboard.row(button1)
    if nexts != -1 and nexts != -2:
        button3 = telebot.types.InlineKeyboardButton(text='Едем дальше!', callback_data="Next")
        keyboard.row(button3)
    caption = "<a href='" + str(place_photo[0][0]) + "'>&#8203;</a>"
    texts = str(place[0][1])
    if nexts != 2 and nexts != -2:
        special = texts.find('❗')
        if special != -1:
            texts = texts[:special - 1]
    line = place[0][0] + '\n' + texts + caption
    if capt == "Первый":
        line = "Первое место нашего путешествия - " + place[0][0] + '\n' + texts + caption
    bot.send_message(message.chat.id, line, parse_mode='HTML', reply_markup=keyboard)


'''
#больше не используется
def scroll_right_excursion(message, id_user: int):
    cursor.execute('select id_excursion from user where id_user = ?', [id_user])
    id_current_excursion = cursor.fetchall()
    cursor.execute('select id_excursion_type from excursion where id_excursion = ?', [id_current_excursion[0][0]])
    id_excursion_type = cursor.fetchall()
    cursor.execute('select id_excursion from excursion where id_excursion_type = ?', [id_excursion_type[0][0]])
    id_excursion = cursor.fetchall()
    for i in range(len(id_excursion)):
        if id_excursion[i][0] == id_current_excursion[0][0]:
            if i == len(id_excursion) - 1:
                update_user_id_excursion(value=id_excursion[0][0], id_user=id_user)
                show_excursions(message, id_excursion=id_excursion[0][0])
            else:
                update_user_id_excursion(value=id_excursion[i + 1][0], id_user=id_user)
                show_excursions(message, id_excursion=id_excursion[i + 1][0])
            break


def scroll_left_excursion(message, id_user: int):
    cursor.execute('select id_excursion from user where id_user = ?', [id_user])
    id_current_excursion = cursor.fetchall()
    cursor.execute('select id_excursion_type from excursion where id_excursion = ?', [id_current_excursion[0][0]])
    id_excursion_type = cursor.fetchall()
    cursor.execute('select id_excursion from excursion where id_excursion_type = ?', [id_excursion_type[0][0]])
    id_excursion = cursor.fetchall()
    for i in range(len(id_excursion)):
        if id_excursion[i][0] == id_current_excursion[0][0]:
            if i == 0:
                update_user_id_excursion(value=id_excursion[len(id_excursion) - 1][0], id_user=id_user)
                show_excursions(message, id_excursion=id_excursion[len(id_excursion) - 1][0])
            else:
                update_user_id_excursion(value=id_excursion[i - 1][0], id_user=id_user)
                show_excursions(message, id_excursion=id_excursion[i - 1][0])
            break
'''


def scroll_right_place(message, id_user: int):
    cursor.execute('select id_excursion, id_place from user where id_user = ?', [id_user])
    current_user_data = cursor.fetchall()
    cursor.execute('select id_place from place where id_excursion = ?', [current_user_data[0][0]])
    id_place = cursor.fetchall()
    for i in range(len(id_place)):
        if current_user_data[0][1] == id_place[i][0]:
            if i == len(id_place) - 1:
                update_user_id_place(value=id_place[0][0], id_user=id_user)
                cursor.execute('select name from place where id_place = ?', [id_place[0][0]])
                place = cursor.fetchall()
                create_buttons(message, place[0][0])
                show_places(message, id_place=id_place[0][0])
            else:
                update_user_id_place(value=id_place[i + 1][0], id_user=id_user)
                cursor.execute('select name from place where id_place = ?', [id_place[i + 1][0]])
                place = cursor.fetchall()
                create_buttons(message, place[0][0])
                show_places(message, id_place=id_place[i + 1][0])
            break


def scroll_left_place(message, id_user: int):
    cursor.execute('select id_excursion, id_place from user where id_user = ?', [id_user])
    current_user_data = cursor.fetchall()
    cursor.execute('select id_place from place where id_excursion = ?', [current_user_data[0][0]])
    id_place = cursor.fetchall()
    for i in range(len(id_place)):
        if current_user_data[0][1] == id_place[i][0]:
            if i == 0:
                update_user_id_place(value=id_place[len(id_place) - 1][0], id_user=id_user)
                cursor.execute('select name from place where id_place = ?', [id_place[len(id_place) - 1][0]])
                place = cursor.fetchall()
                create_buttons(message, place[0][0])
                show_places(message, id_place=id_place[len(id_place) - 1][0])
            else:
                update_user_id_place(value=id_place[i - 1][0], id_user=id_user)
                cursor.execute('select name from place where id_place = ?', [id_place[i - 1][0]])
                place = cursor.fetchall()
                create_buttons(message, place[0][0])
                show_places(message, id_place=id_place[i - 1][0])
            break


def add_to_route(message: types.Message, status: int, id_user: int):
    cursor.execute('select id_place, id_excursion from user where id_user = ?', [id_user])
    user_data = cursor.fetchall()
    if status == 2:
        cursor.execute('select id_place from place where id_excursion = ?', [user_data[0][1]])
        id_place = cursor.fetchall()
        cnt = 0
        for i in id_place:
            cursor.execute('select * from route where id_user = ? and id_place = ?', [id_user, i[0]])
            place_in_route = cursor.fetchall()
            if len(place_in_route) == 0:
                insert_route(user_id=id_user, place_id=i[0])
                cnt += 1
        if cnt == 0:
            #bot.send_message(message.chat.id, 'Экскурсия уже добавлена')
            create_buttons(message, 'Экскурсия уже добавлена')
        else:
            # падежи ставятся правильно до 100
            if cnt < 10:
                if cnt == 1:
                    text = 'место'
                if 2 <= cnt <= 4:
                    text = 'места'
                if cnt > 4:
                    text = 'мест'
            if cnt >=10:
                if 11 <= cnt <= 14:
                    text = 'мест'
                else:
                    if cnt % 10 == 0 or 5 <= cnt % 10 <= 9:
                        text = 'мест'
                    if cnt % 10 == 1:
                        text = 'место'
                    if 2 <= cnt % 10 <= 4:
                        text = 'места'
            #bot.send_message(message.chat.id, 'Добавлено ' + str(cnt) + ' мест')
            create_buttons(message, 'Добавлено ' + str(cnt) + ' ' + text)



    if status == 3:
        cursor.execute('select * from route where id_user = ? and id_place = ?', [id_user, user_data[0][0]])
        id_place = cursor.fetchall()
        if len(id_place) == 0:
            insert_route(user_id=id_user, place_id=user_data[0][0])
            create_buttons(message, 'Добавлено')
        else:
            bot.send_message(message.chat.id, 'Уже добавлено')


def editor(message: types.Message, id_user: int):
    cursor.execute('select id_place from route where id_user = ?', [id_user])
    id_place = cursor.fetchall()
    if len(id_place) == 0:
        bot.send_message(message.chat.id, 'Пусто')
    else:
        places = ""
        for i in id_place:
            cursor.execute('select name from place where id_place = ?', [i[0]])
            place = cursor.fetchall()
            if len(places) == 0:
                places = "- " + place[0][0]
            else:
                places = places + '\n- ' + place[0][0]
        bot.send_message(message.chat.id, places)


@bot.message_handler(content_types=['location'])
def loc(message):
    id_user = message.from_user.id
    cursor.execute('select status from user where id_user = ?', [id_user])
    rows = cursor.fetchall()
    status = rows[0][0]
    lat = message.location.latitude
    long = message.location.longitude
    if status == 4:
        cursor.execute('select id_place from route where id_user = ?', [id_user])
        id_place = cursor.fetchall()
        for p in id_place:
            cursor.execute('select latitude, longitude from place where id_place = ?', [p[0]])
            id_place = cursor.fetchall()
            way = GD((lat, long), (id_place[0][0], id_place[0][1]))
            route.append([way, p[0]])
        if len(route) == 0:
            bot.send_message(message.chat.id, "Маршрут пуст")
            return
        route.sort()
        create_buttons(message.chat.id, 'Stop')
        if len(route) == 1:
            next_place(message, route[0][1], 'Первый', -2)
            bot.send_message(message.chat.id, "Конец пути!")
        if len(route) > 1:
            next_place(message, route[0][1], 'Первый', 2)
        return
    else:
        return


@bot.message_handler(content_types=['text'])
def text(message):
    id_user = message.from_user.id
    cursor.execute('select status from user where id_user = ?', [id_user])
    rows = cursor.fetchall()
    status = rows[0][0]
    if message.text == right_str:
        '''
        if status == 2: #больше не используется
            scroll_right_excursion(message, id_user=id_user)
        '''
        if status == 3:
            scroll_right_place(message, id_user=id_user)
        return

    if message.text == left_str:
        '''
        if status == 2:#больше не используется
            scroll_left_excursion(message, id_user=id_user)
        '''
        if status == 3:
            scroll_left_place(message, id_user=id_user)
        return

    if message.text == back_str:
        if status == 3:
            start(message)
        '''
        if status == 30: #больше не используется
            cursor.execute('select id_excursion from user where id_user = ?', [id_user])
            id_excursion = cursor.fetchall()
            update_user_status(value=2, id_user=id_user)
            create_buttons(message, 'Экскурсии')
           show_excursions(message, id_excursion=id_excursion[0][0])
        '''
        if status == 4:
            cursor.execute('select last_area, id_place, id_excursion from user where id_user = ?', [id_user])
            user_data = cursor.fetchall()
            last_area = user_data[0][0]
            if last_area == 1:
                start(message)
            '''
            if last_area == 2: # не используется
                update_user_status(value=last_area, id_user=id_user)
                create_buttons(message, 'Экскурсии')
                show_excursions(message, id_excursion=user_data[0][2])
            '''
            if last_area == 3:
                update_user_status(value=last_area, id_user=id_user)
                cursor.execute('select name from place where id_place = ?', [user_data[0][1]])
                place = cursor.fetchall()
                create_buttons(message, place[0][0])
                show_places(message, id_place=user_data[0][1])
        return

    '''
    if message.text == show_str:

        if status == 2: #больше не используется
            update_user_status(value=3, id_user=id_user)
            create_buttons(message, 'Места')
            cursor.execute('select id_place, id_excursion from user where id_user = ?', [id_user])
            current_user_data = cursor.fetchall()
            if current_user_data[0][0] is None:
                cursor.execute('select id_place from place where id_excursion = ?', [current_user_data[0][1]])
                id_place = cursor.fetchall()
                update_user_id_place(value=id_place[0][0],id_user=id_user)
                show_places(message, id_place=id_place[0][0])
            if current_user_data[0][0] is not None:
                cursor.execute('select id_excursion from place where id_place = ?', [current_user_data[0][0]])
                id_excursion = cursor.fetchall()
                if id_excursion[0][0] == current_user_data[0][1]:
                    update_user_id_place(value=current_user_data[0][0], id_user=id_user)
                    show_places(message, id_place=current_user_data[0][0])
                else:
                    cursor.execute('select id_place from place where id_excursion = ?', [current_user_data[0][1]])
                    id_place = cursor.fetchall()
                    update_user_id_place(value=id_place[0][0], id_user=id_user)
                    show_places(message, id_place=id_place[0][0])
        '''

    if message.text == select_str:
        add_to_route(message, status=status, id_user=id_user)
        return

    if message.text == add_all:
        add_to_route(message, status=2, id_user=id_user)
        return

    if message.text == delete_str:
        delete_route(id_user=id_user)
        create_buttons(message, 'Удалено')
        return

    if message.text == start_str:
        if status != 4:
            update_user_last_area(value=status, id_user=id_user)
            update_user_status(value=4, id_user=id_user)
            create_buttons(message, 'Ваш маршрут')
            editor(message, id_user=id_user)
            cursor.execute('select id_place from route where id_user = ?', [id_user])
            id_place = cursor.fetchall()
            if len(id_place) != 0:
                bot.send_message(message.chat.id, 'Давайте начнем маршрут с Вашего местонахождения)')
        return

    if message.text == delete_all_str:
        update_user_status(value=6, id_user=id_user)
        create_buttons(message, 'Вы уверены?')
        return

    if message.text == yes_str:
        if status == 6:
            update_user_status(value=4, id_user=id_user)
            cursor.execute('DELETE FROM route WHERE id_user = ?', [id_user])
            con.commit()
            create_buttons(message, 'Ваш маршрут')
            editor(message, id_user=id_user)
        return

    if message.text == no_str:
        if status == 6:
            update_user_status(value=4, id_user=id_user)
            create_buttons(message, 'Ваш маршрут')
            editor(message, id_user=id_user)
            bot.send_message(message.chat.id, 'Давайте начнем маршрут с Вашего местонахождения)')
        return

    bot.send_message(message.chat.id, 'Нет такой команды (╯°□°)╯┻┻')


bot.polling(none_stop=True)
