import sqlite3
import os

db_file = os.path.dirname(os.path.abspath(__file__)) + "/db/db_pla_eve"


class DB:
    def __init__(self):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def add_user(self, user_id, username):
        with self.connection:
            self.cursor.execute('INSERT INTO user (id_user, username) VALUES (?, ?)', (user_id, username))
            self.connection.commit()

    def user_exist(self, user_id: int):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM user WHERE id_user = ?", (user_id,))
            return bool(len(result.fetchall()))

    def get_settings(self, user_id: int):
        with self.connection:
            result = self.cursor.execute("SELECT settings.* FROM settings JOIN user "
                                         "ON settings.id_settings = user.id_settings WHERE id_user = ?", (user_id,))
            return result.fetchone()

    def get_user_cat_pla(self, user_id: int):
        with self.connection:
            result = self.cursor.execute("SELECT category_place.title_en_p, category_place.title_ru_p "
                                         "FROM category_place JOIN user_category_p "
                                         "ON category_place.id_cat_p=user_category_p.id_cat_p WHERE user_category_p.id_user = ?",
                                         (user_id,))
            return result.fetchall()

    def get_cats_places(self):
        with self.connection:
            result = self.cursor.execute("SELECT title_ru_p, title_en_p FROM category_place")
            return result.fetchall()

    def get_cats_events(self):
        with self.connection:
            result = self.cursor.execute("SELECT title_ru_e, title_en_e FROM category_event")
            return result.fetchall()

    def place_exist(self, place_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM place WHERE id_place = ?", (place_id,))
            return bool(len(result.fetchall()))

    def cat_p_exist(self, cat):
        with self.connection:
            result = self.cursor.execute("SELECT id_cat_p FROM category_place WHERE title_en_p = ?", (cat,))
            return bool(len(result.fetchall()))

    def add_place(self, place_id, title, url_im, auth_im, kinds):
        with self.connection:
            self.cursor.execute('INSERT INTO place (id_place, title_place, url_im_p, auth_im_p) VALUES (?, ?, ?, ?)',
                                (place_id, title, url_im, auth_im))
            self.connection.commit()
            cats = kinds.split(",")
            for cat in cats:
                cat_ex = self.cat_p_exist(cat)
                if cat_ex:
                    self.cursor.execute('INSERT INTO place_has_category (id_place, id_cat_p) '
                                        'SELECT ?, id_cat_p FROM category_place WHERE title_en_p = ?', (place_id, cat))
                    self.connection.commit()

    def liked_p_exist(self, user_id, place_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM user_liked_place WHERE id_user = ? and id_place = ?",
                                         (user_id, place_id))
            return bool(len(result.fetchall()))

    def add_liked_pla(self, user_id, place_id):
        with self.connection:
            self.cursor.execute('INSERT INTO user_liked_place (id_place, id_user) VALUES (?, ?)', (place_id, user_id))
            self.connection.commit()

    def settings_exist(self, rad, city, per):
        with self.connection:
            return self.cursor.execute("SELECT id_settings FROM settings WHERE radius = ? AND city = ? AND period = ?",
                                       (rad,city,per))

    def add_setting(self, rad, city, per):
        with self.connection:
            self.cursor.execute('INSERT INTO settings (radius, city, period) VALUES (?, ?, ?)', (rad, city, per))
            self.connection.commit()
            return self.cursor.lastrowid

    def update_city(self, user_id, city):
        with self.connection:
            old_set = self.cursor.execute("SELECT settings.* FROM settings JOIN user WHERE id_user = ?",
                                          (user_id,)).fetchone()
            new_set = self.settings_exist(old_set[1], city, old_set[3]).fetchone()
            if new_set is None:
                new_id = self.add_setting(old_set[1], city, old_set[3])
                self.cursor.execute('UPDATE user SET id_settings = ? WHERE id_user = ?', (new_id, user_id))
            else:
                self.cursor.execute('UPDATE user SET id_settings = ? WHERE id_user = ?', (new_set[0], user_id))
            self.connection.commit()

    def update_radius(self, user_id, rad):
        with self.connection:
            old_set = self.cursor.execute("SELECT settings.* FROM settings JOIN user WHERE id_user = ?",
                                          (user_id,)).fetchone()
            new_set = self.settings_exist(rad, old_set[2], old_set[3]).fetchone()
            if new_set is None:
                new_id = self.add_setting(rad, old_set[2], old_set[3])
            else:
                new_id = new_set[0]
            self.cursor.execute('UPDATE user SET id_settings = ? WHERE id_user = ?', (new_id, user_id))
            self.connection.commit()

    def update_period(self, user_id, per):
        with self.connection:
            old_set = self.cursor.execute("SELECT settings.* FROM settings JOIN user WHERE id_user = ?",
                                          (user_id,)).fetchone()
            new_set = self.settings_exist(old_set[1], old_set[2], per).fetchone()
            if new_set is None:
                new_id = self.add_setting(old_set[1], old_set[2], per)
                self.cursor.execute('UPDATE user SET id_settings = ? WHERE id_user = ?', (new_id, user_id))
            else:
                self.cursor.execute('UPDATE user SET id_settings = ? WHERE id_user = ?', (new_set[0], user_id))
            self.connection.commit()

    def find_liked_pla(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT place.* FROM place JOIN user_liked_place ON place.id_place "
                                       "= user_liked_place.id_place WHERE id_user = ?", (user_id,)).fetchall()

    def delete_fav_pla(self, user_id, place_id):
        with self.connection:
            self.cursor.execute('DELETE FROM user_liked_place WHERE id_user = ? and id_place = ?', (user_id, place_id))
            self.connection.commit()
            return self.cursor.rowcount

    def get_place_cats(self, place_id):
        with self.connection:
            result = self.cursor.execute("SELECT category_place.title_ru_p FROM category_place JOIN place_has_category "
                                         "ON category_place.id_cat_p=place_has_category.id_cat_p "
                                         "WHERE place_has_category.id_place = ?", (place_id,))
            return result.fetchall()

    def add_user_cat_p(self, user_id, title_en):
        with self.connection:
            cat_id = self.cursor.execute("SELECT id_cat_p FROM category_place WHERE title_en_p = ?", (title_en,)).fetchone()
            self.cursor.execute("INSERT INTO user_category_p(id_user, id_cat_p) VALUES(?, ?)",
                                         (user_id, cat_id[0]))
            self.connection.commit()

    def remove_user_cat_p(self, user_id, title_en):
        with self.connection:
            cat_id = self.cursor.execute("SELECT id_cat_p FROM category_place WHERE title_en_p = ?", (title_en,)).fetchone()
            self.cursor.execute("DELETE FROM user_category_p WHERE id_user = ? AND id_cat_p = ?", (user_id, cat_id[0]))
            self.connection.commit()

    def add_user_cat_e(self, user_id, title_en):
        with self.connection:
            cat_id = self.cursor.execute("SELECT id_cat_e FROM category_event WHERE title_en_e = ?", (title_en,)).fetchone()
            self.cursor.execute("INSERT INTO user_category_e(id_user, id_cat_e) VALUES(?, ?)",
                                         (user_id, cat_id[0]))
            self.connection.commit()

    def remove_user_cat_e(self, user_id, title_en):
        with self.connection:
            cat_id = self.cursor.execute("SELECT id_cat_e FROM category_event WHERE title_en_e = ?", (title_en,)).fetchone()
            self.cursor.execute("DELETE FROM user_category_e WHERE id_user = ? AND id_cat_e = ?", (user_id, cat_id[0]))
            self.connection.commit()

    def get_user_cat_eve(self, user_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT category_event.title_en_e, category_event.title_ru_e FROM category_event JOIN user_category_e "
                "ON category_event.id_cat_e=user_category_e.id_cat_e WHERE user_category_e.id_user = ?",
                (user_id,))
            return result.fetchall()

    def event_exist(self, ev_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM event WHERE id_event = ?", (ev_id,))
            return bool(len(result.fetchall()))

    def add_event(self, ev_id, title_event, date, place, description, url_im_e, auth_im_e, site_url, kinds):
        with self.connection:
            self.cursor.execute('INSERT INTO event (id_event, title_event, date, place_e, description, url_im_e, '
                                'auth_im_e, site_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                                (ev_id, title_event, date, place, description, url_im_e, auth_im_e, site_url))
            self.connection.commit()
            for cat in kinds:
                cat_ex = self.cat_e_exist(cat)
                if cat_ex:
                    self.cursor.execute('INSERT INTO event_has_category (id_event, id_cat_e) SELECT ?, id_cat_e '
                                        'FROM category_event WHERE title_en_e = ?', (ev_id, cat))
                    self.connection.commit()

    def liked_e_exist(self, user_id, event_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM user_liked_event WHERE id_user = ? and id_event = ?",
                                         (user_id, event_id))
            return bool(len(result.fetchall()))

    def add_liked_ev(self, user_id, event_id):
        with self.connection:
            self.cursor.execute('INSERT INTO user_liked_event (id_user, id_event) VALUES (?, ?)', (user_id, event_id))
            self.connection.commit()

    def cat_e_exist(self, cat):
        with self.connection:
            result = self.cursor.execute("SELECT id_cat_e FROM category_event WHERE title_en_e = ?", (cat,))
            return bool(len(result.fetchall()))

    def find_liked_ev(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT event.* FROM event JOIN user_liked_event "
                                       "ON event.id_event = user_liked_event.id_event WHERE id_user = ?",
                                       (user_id,)).fetchall()

    def get_event_cats(self, event_id):
        with self.connection:
            result = self.cursor.execute("SELECT category_event.title_ru_e FROM category_event JOIN event_has_category "
                                         "ON category_event.id_cat_e=event_has_category.id_cat_e "
                                         "WHERE event_has_category.id_event = ?", (event_id,))
            return result.fetchall()

    def delete_fav_ev(self, user_id, event_id):
        with self.connection:
            self.cursor.execute('DELETE FROM user_liked_event WHERE id_user = ? and id_event = ?', (user_id, event_id))
            self.connection.commit()
            return self.cursor.rowcount
