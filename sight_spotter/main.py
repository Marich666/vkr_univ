import re
from database import DB
import API_requests
import keyboard
from place import Place
from event import Event
from user import User
import resize
import requests
import time
import hashlib
import urllib.parse
import datetime
import pytz
from timezonefinder import TimezoneFinder

TOKEN = ''
URL = 'https://api.telegram.org/bot'

is_city = False
is_radius = False
is_period = False

kinds_exp_p = ""
kinds_exp_e = ""

patImNamePla = r'value&quot;.*&quot;(.*?)&quot;'
patAuName = r'"imageinfo":.*"user":"(.*?)"'
patExpPlace = r'(.*?;.*?;.*?);'
patExpEv = r'(.*?;.*?;.*?;.*?);'

page = 0
list_pla = []
list_fav_pla = []
list_fav_ev = []
dict_kinds_p = {}
dict_kinds_e = {}
lon_exp = 0
lat_exp = 0
rad_exp = 0
per_exp = 0
is_pla = False
is_first = True
user = User(-1, "", [], [])
tf = TimezoneFinder()
timezone = pytz.timezone('Europe/Moscow')
db = DB()
ev = Event()


def get_updates(offset=0):
    result = requests.get(f'{URL}{TOKEN}/getUpdates?offset={offset}').json()
    return result['result']


def send_message(data):
    requests.post(f'{URL}{TOKEN}/sendMessage', data=data)


def send_photo(files, data):
    requests.post(f'{URL}{TOKEN}/sendPhoto', files=files, data=data)


def reply_keyboard(chat_id, text, url):
    global is_pla, is_city, is_period, is_radius, kinds_exp_p, kinds_exp_e, ev, list_fav_ev, list_fav_pla, page
    if (text == "Используйте интерактивную клавиатуру" or text == "Конец"
            or text == "Запрос не распознан, попробуйте еще раз"
            or text == "По заданным критериям ничего не найдено, попробуйте изменить радиус поиска"
            or text == "Вас приветствует бот для поиска достопримечательностей и событий!\nИспользуйте интерактивную клавиатуру"):
        ev.reset()
        is_city = False
        is_radius = False
        is_period = False
        list_fav_pla.clear()
        list_fav_ev.clear()
        list_pla.clear()
        page = 0
        send_message(keyboard.main_menu(chat_id, text))
    elif text == "Выберите параметр для изменения":
        message = f"Текущие настройки:\nГород: {user.city}\nРадиус: {user.rad} (м)\nПериод: {user.period} (дни)\n" \
                  f"Категории мест: "
        #категории из БД
        cats = db.get_user_cat_pla(chat_id)
        for cat in cats:
            message += cat[1] + ", "
        message += "\nКатегории событий: "
        cats.clear()
        cats = db.get_user_cat_eve(chat_id)
        for cat in cats:
            message += cat[1] + ", "
        send_message({'chat_id': chat_id, 'text': message})
        is_city = False
        is_radius = False
        is_period = False
        send_message(keyboard.param_menu(chat_id, text))
    elif text == "Введите город":
        is_city = True
        is_radius = False
        is_period = False
        requests.post(f'{URL}{TOKEN}/sendMessage', data=keyboard.back_and_main(chat_id, text))
    elif text == "Введите радиус поиска в метрах":
        is_radius = True
        is_city = False
        is_period = False
        requests.post(f'{URL}{TOKEN}/sendMessage', data=keyboard.back_and_main(chat_id, text))
    elif text == "Введите период поиска в днях":
        is_city = False
        is_radius = False
        is_period = True
        requests.post(f'{URL}{TOKEN}/sendMessage', data=keyboard.back_and_main(chat_id, text))
    elif text == "Выберите категорию":
        requests.post(f'{URL}{TOKEN}/sendMessage', data=keyboard.categ_liked(chat_id, text))
    elif text == "Выберите тип поиска мест":
        is_pla = True
        send_message(keyboard.type_search_p(chat_id, text))
    elif text == "Выберите тип поиска событий":
        is_pla = False
        send_message(keyboard.type_search_e(chat_id, text))
    elif text == "Выберите категории поиска мест":
        kinds_exp_p = ""
        send_message(keyboard.categ_p(chat_id, text))
    elif text == "Выберите категории поиска событий":
        kinds_exp_e = ""
        send_message(keyboard.categ_e(chat_id, text))
    elif text == "Выберите категории событий (выбор категории, существующей в избранном, удалит ее из избранного)":
        kinds_exp_e = ""
        send_message(keyboard.categ_liked_e(chat_id, text))
    elif text == "Выберите категории мест (выбор категории, существующей в избранном, удалит ее из избранного)":
        kinds_exp_p = ""
        send_message(keyboard.categ_liked_p(chat_id, text))
    elif url != "" and len(list_fav_pla) > 0:
        files = resize.check_size_im(url)
        send_photo(files=files, data=keyboard.browsing_liked_p_im(chat_id, text))
    elif len(list_fav_pla) > 0:
        send_message(keyboard.browsing_liked_p(chat_id, text))
    elif url != "" and len(list_fav_ev) > 0:
        files = resize.check_size_im(url)
        send_photo(files=files, data=keyboard.browsing_liked_e_im(chat_id, text))
    elif len(list_fav_ev) > 0:
        send_message(keyboard.browsing_liked_e(chat_id, text))
    elif url != "" and is_pla:
        files = resize.check_size_im(url)
        send_photo(files=files, data=keyboard.browsing_p_im(chat_id, text))
    elif url != "":
        files = resize.check_size_im(url)
        send_photo(files=files, data=keyboard.browsing_e_im(chat_id, text))
    elif is_pla:
        send_message(keyboard.browsing_p(chat_id, text))
    else:
        send_message(keyboard.browsing_e(chat_id, text))


def exp_places_info(chat_id, info):
    global lat_exp, lon_exp, rad_exp
    info_sp = re.search(patExpPlace, info).group(1).split(";")
    if get_info(chat_id, info_sp):
        #предложение выбора категорий
        reply_keyboard(chat_id, "Выберите категории поиска мест", "")
    else:
        return


def exp_ev_inf(chat_id, info):
    global lat_exp, lon_exp, rad_exp, per_exp
    match = re.search(patExpEv, info)
    if match:
        info_sp = match.group(1).split(";")
        if get_info(chat_id, info_sp):
            if info_sp[3] == "":
                per_exp = user.period
                per_exp = 7
            else:
                try:
                    per_exp = abs(int(info_sp[3]))
                except TypeError:
                    send_message({'chat_id': chat_id, 'text': "Период поиска указан некорректно, проверьте правильность ввода"})  # ???
                    return
            # предложение выбора категорий
            reply_keyboard(chat_id, "Выберите категории поиска событий", "")
        else:
            return


def get_info(chat_id, info_sp):
    global lat_exp, lon_exp, rad_exp, per_exp
    for i in info_sp:
        i.strip()
        i.replace(" ", "_")
    if info_sp[0] == "":
        city_exp = user.city
    else:
        city_exp = info_sp[0]
    if info_sp[1] == "":
        answer = API_requests.get_city_inf(city_exp)
        lon = answer.get('lon')
        lat = answer.get('lat')
        if lon is not None and lat is not None:
            try:
                lon_exp = float(lon)
                lat_exp = float(lat)
            except TypeError:
                send_message({'chat_id': chat_id, 'text': "Не удалось получить координаты города,"
                                                          " проверьте правильность ввода"})
                return False
        else:
            send_message({'chat_id': chat_id, 'text': "Не удалось получить координаты города, проверьте правильность ввода"})
            return False
    else:
        #поиск координат адреса в osm
        addr = API_requests.get_addr_inf(info_sp[0], info_sp[1])
        try:
            lat_exp = float(addr['lat'])
            lon_exp = float(addr['lon'])
            print(lat_exp," ",lon_exp)
        except TypeError:
            send_message({'chat_id': chat_id, 'text': "Не удалось получить координаты адреса, "
                                                      "проверьте правильность ввода"})
            return False
    if info_sp[2] == "":
        rad_exp = user.rad
    else:
        try:
            rad_exp = float(info_sp[2])
        except TypeError:
            send_message({'chat_id': chat_id, 'text': "Радиус поиска указан некорректно, проверьте правильность ввода"})
            return False
    return True


def show_places(chat_id):
    global page
    if len(list_pla) == 0:
        reply_keyboard(chat_id, "По заданным критериям ничего не найдено, попробуйте изменить радиус поиска", "")
    elif page < len(list_pla):
        if list_pla[page].wikidata != "":
            im_wiki = API_requests.get_im_info(list_pla[page].wikidata)
            match_im = re.search(patImNamePla, im_wiki)
            if match_im:
                print(match_im.group(1))
                filename = match_im.group(1).replace(" ", "_")
                if filename.find("\\u") != -1:
                    filename = filename.encode().decode('unicode-escape')
                    print(filename)
                md5_hash = filename.encode(encoding='UTF-8', errors='strict')
                hash_im = hashlib.md5(md5_hash).hexdigest()
                print(hash)
                encoded_filename = urllib.parse.quote(filename)  ## чтобы неиспользуемые в url символы были заменены процентным представлением
                list_pla[page].im_url = f"https://upload.wikimedia.org/wikipedia/commons/{hash_im[0]}/{hash_im[0]}{hash_im[1]}/{filename}"
                auth_wiki = API_requests.get_im_auth(encoded_filename)
                match_au = re.search(patAuName, auth_wiki)
                if match_au:
                    auth_im = (match_au.group(1))
                    if auth_im.find("\\u") != -1:
                        auth_im = auth_im.encode().decode('unicode-escape')
                    list_pla[page].im_auth = auth_im
                    reply_keyboard(chat_id,
                                   f'Название: {list_pla[page].name}\nРасстояние(м): {list_pla[page].dist}\nТеги: '
                                   f'{list_pla[page].kinds}\n\nPhoto by: {list_pla[page].im_auth}', list_pla[page].im_url)
                    page += 1
                else:
                    reply_keyboard(chat_id,
                                   f'Название: {list_pla[page].name}\nРасстояние(м): {list_pla[page].dist}\nТеги: '
                                   f'{list_pla[page].kinds}', list_pla[page].im_url)
                    page += 1
            else:
                reply_keyboard(chat_id, f'Название: {list_pla[page].name}\nРасстояние(м): {list_pla[page].dist}\nТеги: '
                                        f'{list_pla[page].kinds}', '')
                page += 1
        else:
            reply_keyboard(chat_id, f'Название: {list_pla[page].name}\nРасстояние(м): {list_pla[page].dist}\nТеги: '
                                    f'{list_pla[page].kinds}', '')
            page += 1
    elif page == len(list_pla):
        list_pla.clear()
        page = 0
        reply_keyboard(chat_id, f'Конец', '')


def show_fav_places(chat_id):
    global page
    if len(list_fav_pla) == 0:
        send_message({'chat_id': chat_id, 'text': "Тут пока пусто"})
    elif page < len(list_fav_pla):
        cats = db.get_place_cats(list_fav_pla[page][0])
        print(list_fav_pla[page][0])
        print(cats)
        mes_cats = ""
        for cat in cats:
            mes_cats += cat[0] + ", "
        if mes_cats == "":
            message = f'Название: {list_fav_pla[page][1]}\n\nPhoto by: {list_fav_pla[page][3]}'
        else:
            message = f'Название: {list_fav_pla[page][1]}\nКатегории: {mes_cats}\n\nPhoto by: {list_fav_pla[page][3]}'
        reply_keyboard(chat_id, message, list_fav_pla[page][2])
        page += 1
    else:
        list_fav_pla.clear()
        page = 0
        reply_keyboard(chat_id, f'Конец', '')


def check_fav_places(chat_id):
    global page, list_fav_pla
    list_fav_pla = db.find_liked_pla(chat_id)
    page = 0
    show_fav_places(chat_id)


def check_fav_e(chat_id):
    global page, list_fav_ev
    list_fav_ev = db.find_liked_ev(chat_id)
    page = 0
    fav_e_show(chat_id)


def fav_e_show(chat_id):
    global page
    if len(list_fav_ev) == 0:
        send_message({'chat_id': chat_id, 'text': "Тут пока пусто"})
    elif page < len(list_fav_ev):
        message = f'Название: {list_fav_ev[page][1]}\n\nМесто проведения: {list_fav_ev[page][2]}\n\n' \
                  f'Описание: {list_fav_ev[page][3]}\n\n'
        cats = db.get_event_cats(list_fav_ev[page][0])
        print(list_fav_ev[page][0])
        print(cats)
        mes_cats = ""
        for cat in cats:
            mes_cats += cat[0] + ", "
        if mes_cats != "":
            message += f'Категории: {mes_cats}\n\n'
        message += f'Даты: {list_fav_ev[page][4]}\n\nURL: {list_fav_ev[page][7]}\n\n'
        if list_fav_ev[page][6] !="":
            message += f'Photo by: {list_fav_ev[page][6]}'
        print(list_fav_ev[page][5])
        reply_keyboard(chat_id, message, list_fav_ev[page][5])
        page += 1
    else:
        list_fav_ev.clear()
        page = 0
        reply_keyboard(chat_id, f'Конец', '')


def ev_search(chat_id, kinds, lon, lat, rad):
    global tf, timezone
    print(kinds)
    timezone_str = tf.timezone_at(lng=lon_exp, lat=lat_exp)
    timezone = pytz.timezone(timezone_str)
    since = datetime.datetime.now().timestamp()
    print(since)
    till = (datetime.datetime.now() + datetime.timedelta(days=per_exp)).timestamp()
    event = API_requests.get_event_inf(since, till, kinds, lon, lat, rad)
    if event.get("count", 0) != 0:
        show_ev(chat_id, event)
    else:
        reply_keyboard(chat_id, "По заданным критериям ничего не найдено, попробуйте изменить радиус поиска", "")


def places_geo(chat_id, loc):
    lat = loc['latitude']
    lon = loc['longitude']
    if len(user.kinds_p) > 0:
        kinds = ""
        for kind in user.kinds_p:
            kinds += kind+","
    else:
        kinds = ""
    places_search(chat_id, API_requests.get_place_inf(user.rad, lon, lat, kinds))


def events_geo(chat_id, loc):
    lat = loc['latitude']
    lon = loc['longitude']
    if len(user.kinds_e) > 0:
        kinds = ""
        for kind in user.kinds_e:
            kinds += kind + ","
    else:
        kinds = ""
    kinds = kinds.strip(",")
    ev_search(chat_id, kinds, lon, lat, user.rad)


def places_search(chat_id, answer):
    places = answer.get('features')
    list_pla.clear()
    for i in range(0, len(places), 1):
        pla = places[i].get("properties")
        list_pla.append(Place(pla.get('xid'),
                              pla.get('name'),
                              round(float(pla.get('dist'))),
                              pla.get('kinds'),
                              pla.get('wikidata')))
    show_places(chat_id)


def show_ev(chat_id, events):
    global ev, tf
    event = events.get('results')[0]
    print(event)
    place_id = event.get('place', {}).get('id')
    if place_id is not None:
        place = API_requests.get_event_place_name(place_id).get("title")
    else:
        place = ""
    dates = event.get('dates')
    max_st = timezone.localize(datetime.datetime.now())
    print(max_st)
    max_end = max_st
    for date in dates:
        try:
            start = datetime.datetime.utcfromtimestamp(date['start'])
            start = pytz.utc.localize(start).astimezone(timezone)
            if start > max_st:
                max_st = start
                print(max_st)
        except OSError:
            print("err")
        try:
            end = datetime.datetime.utcfromtimestamp(date['end'])
            end = pytz.utc.localize(end).astimezone(timezone)
            if end > max_end:
                max_end = end
                print(max_end)
        except OSError:
            continue
    dates = ""
    future_date = datetime.datetime.now(timezone) + datetime.timedelta(days=365*5)
    if max_st == max_end <= timezone.localize(datetime.datetime.now()):
        dates = "бессрочно"
    elif max_st == max_end and timezone.localize(datetime.datetime.now()) <= max_end < future_date:
        dates = max_st.strftime('%H:%M %d.%m.%Y')
    else:
        if max_st > datetime.datetime.now(timezone):
            dates = "c " + max_st.strftime('%H:%M %d.%m.%Y') + " "
        if datetime.datetime.now(timezone) < max_end < future_date:
            dates += "по " + max_end.strftime('%H:%M %d.%m.%Y')
        else:
            dates += "бессрочно"

    ev = Event(event.get('id'), event.get('title'), place, event.get('description'), dates,
               event.get('images', [])[0].get("image"), event.get('images', [])[0].get("source").get("name"),
               event.get('site_url'), events.get('next'), event.get("categories"))

    message = f"Название: {ev.title}\n\n"
    if ev.place != "":
        message += f"Место проведения: {ev.place}\n\n"
    message += f"Описание: {ev.descr}\n\nКатегории: "
    for cat in ev.categ:
        key = next((k for k, v in dict_kinds_e.items() if v == cat), "")
        message += key + ","
    message += f"\n\nДаты: {ev.dates}\n\nURL: {ev.site_url}"
    if ev.im_auth != "":
        message += "\n\nPhoto: " + ev.im_auth
    reply_keyboard(chat_id, message, ev.im_url)


def handle_message(chat_id, message):
    global page, kinds_exp_p, kinds_exp_e, is_city, is_pla, user
    message_l = message.lower()
    if message_l == "❤️" and len(list_pla) > 0:
        if not db.place_exist(list_pla[page-1].id_pla):
            db.add_place(list_pla[page-1].id_pla, list_pla[page-1].name, list_pla[page-1].im_url,
                         list_pla[page-1].im_auth, list_pla[page-1].kinds)
        if db.liked_p_exist(chat_id, list_pla[page-1].id_pla):
            send_message({'chat_id': chat_id, 'text': "Это место уже есть в избранном"})
        else:
            db.add_liked_pla(chat_id, list_pla[page-1].id_pla)
            send_message({'chat_id': chat_id, 'text': f'{list_pla[page-1].name} добавлен (-а,-о) в избранное'})
    elif message_l == "🧡" and ev.id_ev != "":
        if not db.event_exist(ev.id_ev):
            db.add_event(ev.id_ev, ev.title, ev.dates, ev.place, ev.descr,
                         ev.im_url, ev.im_auth, ev.site_url, ev.categ)
        if db.liked_e_exist(chat_id, ev.id_ev):
            send_message({'chat_id': chat_id, 'text': "Это событие уже есть в избранном"})
        else:
            db.add_liked_ev(chat_id, ev.id_ev)
            send_message({'chat_id': chat_id, 'text': f'{ev.title} добавлен (-а,-о) в избранное'})
    elif message_l == "места":
        reply_keyboard(chat_id, 'Выберите тип поиска мест', '')
    elif message_l == "события":
        reply_keyboard(chat_id, 'Выберите тип поиска событий', '')
    elif message_l == "расширенный поиск мест":
        send_message({'chat_id': chat_id, 'text': 'Введите данные в формате "Город; Адрес; Радиус поиска (м);"\n'
                                                  'При отсутствии одного из критериев, оставьте поле пустым, '
                                                  'но сохраните ;'})
    elif message_l == "расширенный поиск событий":
        send_message({'chat_id': chat_id, 'text': 'Введите данные в формате "Город; Адрес; Радиус поиска (м); '
                                                  'Период (д);"\nПри отсутствии одного из критериев, оставьте поле '
                                                  'пустым, но сохраните ;'})
    elif message_l == "город":
        reply_keyboard(chat_id, "Введите город", '')
    elif message_l == "радиус":
        reply_keyboard(chat_id, "Введите радиус поиска в метрах", '')
    elif message_l == "период":
        reply_keyboard(chat_id, "Введите период поиска в днях", '')
    elif message_l == "избранное":
        reply_keyboard(chat_id, "Выберите категорию", '')
    elif message_l == "категории мест":
        reply_keyboard(chat_id, "Выберите категории мест "
                                "(выбор категории, существующей в избранном, удалит ее из избранного)", '')
    elif message_l == "категории событий":
        reply_keyboard(chat_id,
                       "Выберите категории событий "
                       "(выбор категории, существующей в избранном, удалит ее из избранного)",
                       '')
    elif message == "❤️ Места ❤️":
        check_fav_places(chat_id)
    elif message == "❤️ Далее ❤️" and len(list_fav_pla)>0:
        show_fav_places(chat_id)
    elif message == "🧡 События 🧡":
        check_fav_e(chat_id)
    elif message == "🧡️ Далее 🧡️" and len(list_fav_ev) > 0:
        fav_e_show(chat_id)
    elif message == "Удалить место" and len(list_fav_pla) > 0:
        if db.delete_fav_pla(chat_id, list_fav_pla[page-1][0]) == 0:
            send_message({'chat_id': chat_id, 'text': f"{list_fav_pla[page - 1][1]} уже удален (-а, -о)"})
        else:
            send_message({'chat_id': chat_id, 'text': f"{list_fav_pla[page-1][1]} удален (-а, -о) из избранного"})
    elif message == "Удалить событие" and len(list_fav_ev)>0:
        if db.delete_fav_ev(chat_id, list_fav_ev[page-1][0]) == 0:
            send_message({'chat_id': chat_id, 'text': f"{list_fav_ev[page - 1][1]} уже удален (-а, -о)"})
        else:
            send_message({'chat_id': chat_id, 'text': f"{list_fav_ev[page-1][1]} удален (-а, -о) из избранного"})
    elif message_l in ("настройки", "назад"):
        reply_keyboard(chat_id, 'Выберите параметр для изменения', '')
    elif is_city:
        answer = API_requests.get_city_inf(message.strip())
        print(answer)
        if "error" not in answer:
            db.update_city(chat_id, message)
            send_message({'chat_id': chat_id, 'text': "Город изменен"})
            user.city = message
            reply_keyboard(chat_id, 'Выберите параметр для изменения', '')
        else:
            send_message({'chat_id': chat_id, 'text': "Город не найден, проверьте правильность написания"})
    elif is_radius:
        try:
            rad = int(message)
            if 0 < rad <= 15000:
                db.update_radius(chat_id, rad)
                send_message({'chat_id': chat_id, 'text': "Радиус поиска изменен"})
                user.rad = rad
                reply_keyboard(chat_id, 'Выберите параметр для изменения', '')
            else:
                send_message({'chat_id': chat_id, 'text': "Радиус должен быть натуральным числом от 1 до 15000"})
        except ValueError:
            send_message({'chat_id': chat_id, 'text': "Радиус должен быть натуральным числом от 1 до 15000"})
    elif is_period:
        try:
            per = int(message)
            if 0 < per <= 31:
                db.update_period(chat_id, per)
                send_message({'chat_id': chat_id, 'text': "Период поиска изменен"})
                user.period = per
                reply_keyboard(chat_id, 'Выберите параметр для изменения', '')
            else:
                send_message({'chat_id': chat_id, 'text': "Период должен быть натуральным числом от 1 до 31"})
        except ValueError:
            send_message({'chat_id': chat_id, 'text': "Период должен быть натуральным числом от 1 до 31"})
    elif message_l == "далее" and is_pla:
        show_places(chat_id)
    elif message_l == "далее":
        print(ev.next_e)
        if ev.next_e is not None:
            r = requests.get(ev.next_e)
            show_ev(chat_id, r.json())
        else:
            reply_keyboard(chat_id, f'Конец', '')
    elif message_l == "места из профиля":
        if len(user.kinds_p) > 0:
            for kind in user.kinds_p:
                kinds_exp_p += kind + ","
    elif message_l == "события из профиля":
        if len(user.kinds_e) > 0:
            for kind in user.kinds_e:
                kinds_exp_e += kind + ","
    elif message_l in ("спорт", "природа", "архитектура", "культура", "история", "религия"):
        kind_in = kinds_exp_p.find(dict_kinds_p[message_l])
        print(kind_in)
        if kind_in == -1:
            kinds_exp_p += dict_kinds_p[message_l] + ","
    elif message_l in ("концерты", "спектакли", "выставки", "мода", "развлечения", "активный отдых"):
        kind_in = kinds_exp_e.find(dict_kinds_e[message_l])
        print(kind_in)
        if kind_in == -1:
            kinds_exp_e += dict_kinds_e[message_l] + ","
    elif message_l == "все места":
        kind_in = kinds_exp_p.find('interesting_places')
        if kind_in == -1:
            kinds_exp_p += "interesting_places,"
        kind_in = kinds_exp_p.find('sport')
        if kind_in == -1:
            kinds_exp_p += "sport,"
    elif message_l == "все события":
        kinds_exp_e = ""
    elif message_l == "поиск достопримечательностей":
        list_pla.clear()
        places_search(chat_id, API_requests.get_place_inf(rad_exp, lon_exp, lat_exp, kinds_exp_p))
    elif message_l == "поиск событий":
        ev.reset()
        ev_search(chat_id, kinds_exp_e.strip(","), lon_exp, lat_exp, rad_exp)
    elif message_l == "подтвердить изменения\nкатегорий мест":
        if kinds_exp_p != "":
            kinds_exp_p = kinds_exp_p.strip(",")
            cats = kinds_exp_p.split(",")
            old_user_cats = db.get_user_cat_pla(chat_id)
            old_user_cats_en = []
            for cat in old_user_cats:
                old_user_cats_en.append(cat[0])
            for cat in cats:
                if cat in old_user_cats_en:
                    db.remove_user_cat_p(chat_id, cat)
                else:
                    db.add_user_cat_p(chat_id, cat)
            send_message({'chat_id': chat_id, 'text': "Категории мест изменены"})
            user.kinds_p.clear()
            kinds_p = db.get_user_cat_pla(chat_id)
            for kind in kinds_p:
                user.kinds_p.append(kind[0])
            kinds_exp_p = ""
            reply_keyboard(chat_id, 'Выберите параметр для изменения', '')
        else:
            reply_keyboard(chat_id, 'Выберите параметр для изменения', '')
    elif message_l == "подтвердить изменения\nкатегорий событий":
        if kinds_exp_e != "":
            kinds_exp_e = kinds_exp_e.strip(",")
            cats = kinds_exp_e.split(",")
            old_user_cats = db.get_user_cat_eve(chat_id)
            old_user_cats_en = []
            for cat in old_user_cats:
                old_user_cats_en.append(cat[0])
            for cat in cats:
                if cat in old_user_cats_en:
                    db.remove_user_cat_e(chat_id, cat)
                else:
                    db.add_user_cat_e(chat_id, cat)
            send_message({'chat_id': chat_id, 'text': "Категории событий изменены"})
            user.kinds_e.clear()
            kinds_e = db.get_user_cat_eve(chat_id)
            for kind in kinds_e:
                user.kinds_e.append(kind[0])
            kinds_exp_e = ""
        reply_keyboard(chat_id, 'Выберите параметр для изменения', '')
    elif re.search(patExpEv, message_l):
        is_pla = False
        kinds_exp_e = ""
        exp_ev_inf(chat_id, message)
    elif re.search(patExpPlace, message_l):
        is_pla = True
        list_pla.clear()
        kinds_exp_p = ""
        exp_places_info(chat_id, message)
    elif message_l == "на главную":
        reply_keyboard(chat_id, 'Используйте интерактивную клавиатуру', '')
    elif message_l == "/start":
        reply_keyboard(chat_id, 'Вас приветствует бот для поиска достопримечательностей и событий!\nИспользуйте интерактивную клавиатуру', '')
    else:
        reply_keyboard(chat_id, 'Запрос не распознан, попробуйте еще раз', '')


def auth_and_settings(chat_id, name):
    global user
    kinds_p = db.get_cats_places()
    for kind in kinds_p:
        dict_kinds_p[kind[0]] = kind[1]
    kinds_e = db.get_cats_events()
    for kind in kinds_e:
        dict_kinds_e[kind[0]] = kind[1]
    if db.user_exist(chat_id):
        settings = db.get_settings(chat_id)
        kinds_p = db.get_user_cat_pla(chat_id)
        kinds_p_d =[]
        if kinds_p is not None:
            for kind in kinds_p:
                kinds_p_d.append(kind[0])
        kinds_e = db.get_user_cat_eve(chat_id)
        kinds_e_d = []
        if kinds_e is not None:
            for kind in kinds_e:
                kinds_e_d.append(kind[0])
        user = User(chat_id, name,
                    kinds_p_d, kinds_e_d, settings[1], settings[2], settings[3])
    else:
        db.add_user(chat_id, name)
        user = User(chat_id, name, [], [])


def run():
    global is_first
    update_id = get_updates()[-1]['update_id'] # Сохраняем ID последнего отправленного сообщения боту
    while True:
        time.sleep(2)
        messages = get_updates(update_id)# Получаем обновления
        for message in messages:
        # Если в обновлении есть ID больше чем ID последнего сообщения, значит пришло новое сообщение
            if update_id < message['update_id']:
                if is_first and message.get("message"):
                    auth_and_settings(message['message']['chat']['id'], message['message']['chat']['username'])
                    is_first = False
                elif message.get("my_chat_member") and user.id_user == -1:
                    auth_and_settings(message['my_chat_member']['from']['id'],
                                      message['my_chat_member']['from']['username'])
                    is_first = False
                    continue
                update_id = message['update_id']# Сохраняем ID последнего отправленного сообщения боту
                if user_message := message['message'].get('text'): # Проверим, есть ли текст в сообщении
                    handle_message(message['message']['chat']['id'], user_message) # Отвечаем
                if user_location := message['message'].get('location'): # Проверим, если ли location в сообщении
                    if is_pla:
                        places_geo(message['message']['chat']['id'], user_location)
                    else:
                        events_geo(message['message']['chat']['id'], user_location)


if __name__ == '__main__':
    run()
