class User:
    def __init__(self, id_user, name, kinds_p, kinds_e, rad=1000, city="Москва", period=7):
        self.id_user = id_user
        self.name = name
        self.kinds_p = kinds_p
        self.kinds_e = kinds_e
        self.rad = rad
        self.city = city
        self.period = period
