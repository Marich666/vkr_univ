import json


def main_menu(chat_id, text):
    reply_markup = {"keyboard": [["Места", "События"], ["Избранное", "Настройки"]], "resize_keyboard": True,
                    "one_time_keyboard": False}
    return {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}


def param_menu(chat_id, text):
    reply_markup = {"keyboard": [["Город", "Радиус", "Период"], ["Категории мест", "Категории событий"],
                                 ["На главную"]], "resize_keyboard": True, "one_time_keyboard": False}
    return {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}


def back_and_main(chat_id, text):
    reply_markup = {"keyboard": [["Назад"], ["На главную"]], "resize_keyboard": True, "one_time_keyboard": False}
    return {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}


def categ_liked(chat_id, text):
    reply_markup = {"keyboard": [["❤️ Места ❤️", "🧡 События 🧡"], ["На главную"]], "resize_keyboard": True,
                    "one_time_keyboard": False}
    return {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}


def type_search_p(chat_id, text):
    reply_markup = {"keyboard": [[{"request_location": True, "text": "Быстрый поиск мест"}],
                                 ["Расширенный поиск мест"], ["На главную"]], "resize_keyboard": True,
                    "one_time_keyboard": True}
    return {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}


def type_search_e(chat_id, text):
    reply_markup = {
        "keyboard": [[{"request_location": True, "text": "Быстрый поиск событий"}], ["Расширенный поиск событий"],
                     ["На главную"]], "resize_keyboard": True, "one_time_keyboard": True}
    return {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}


def categ_p(chat_id, text):
    reply_markup = {"keyboard": [["Природа", "Спорт"],["Архитектура", "Культура"],["История", "Религия"],
                                 ["Места из профиля", "Все места"], ["Поиск достопримечательностей"],["На главную"]],
                    "resize_keyboard": True, "one_time_keyboard": False}
    return {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}


def categ_e(chat_id, text):
    reply_markup = {"keyboard": [["Концерты", "Спектакли"], ["Выставки", "Мода"], ["Развлечения", "Активный отдых"],
                                 ["События из профиля", "Все события"], ["Поиск событий"], ["На главную"]],
                    "resize_keyboard": True, "one_time_keyboard": False}
    return {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}


def categ_liked_e(chat_id, text):
    reply_markup = {"keyboard": [["Концерты", "Спектакли"], ["Выставки", "Мода"], ["Развлечения", "Активный отдых"],
                                 ["Подтвердить изменения\nкатегорий событий"], ["На главную"]],
                    "resize_keyboard": True, "one_time_keyboard": False}
    return {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}


def categ_liked_p(chat_id, text):
    reply_markup = {"keyboard": [["Природа", "Спорт"], ["Архитектура", "Культура"], ["История", "Религия"],
                                 ["Подтвердить изменения\nкатегорий мест"], ["На главную"]],
                    "resize_keyboard": True, "one_time_keyboard": False}
    return {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}


def browsing_liked_p_im(chat_id, text):
    reply_markup = {"keyboard": [["Удалить место", "❤️ Далее ❤️"], ["На главную"]],
                    "resize_keyboard": True, "one_time_keyboard": False}
    return {'chat_id': chat_id, 'caption': text, 'reply_markup': json.dumps(reply_markup)}


def browsing_liked_p(chat_id, text):
    reply_markup = {"keyboard": [["Удалить место", "❤️ Далее ❤️"], ["На главную"]],
                    "resize_keyboard": True, "one_time_keyboard": False}
    return {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}


def browsing_liked_e_im(chat_id, text):
    reply_markup = {"keyboard": [["Удалить событие", "🧡️ Далее 🧡️"], ["На главную"]],
                    "resize_keyboard": True, "one_time_keyboard": False}
    return {'chat_id': chat_id, 'caption': text, 'reply_markup': json.dumps(reply_markup)}


def browsing_liked_e(chat_id, text):
    reply_markup = {"keyboard": [["Удалить событие", "🧡️ Далее 🧡️"], ["На главную"]],
                    "resize_keyboard": True, "one_time_keyboard": False}
    return {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}


def browsing_p_im(chat_id, text):
    reply_markup = {"keyboard": [["❤️", "Далее"], ["На главную"]], "resize_keyboard": True,
                    "one_time_keyboard": False}
    return {'chat_id': chat_id, 'caption': text, 'reply_markup': json.dumps(reply_markup)}


def browsing_p(chat_id, text):
    reply_markup = {"keyboard": [["❤️", "Далее"], ["На главную"]], "resize_keyboard": True,
                    "one_time_keyboard": False}
    return {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}


def browsing_e_im(chat_id, text):
    reply_markup = {"keyboard": [["🧡", "Далее"], ["На главную"]], "resize_keyboard": True, "one_time_keyboard": False}
    return {'chat_id': chat_id, 'caption': text, 'reply_markup': json.dumps(reply_markup)}


def browsing_e(chat_id, text):
    reply_markup = {"keyboard": [["🧡", "Далее"], ["На главную"]], "resize_keyboard": True, "one_time_keyboard": False}
    return {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}
