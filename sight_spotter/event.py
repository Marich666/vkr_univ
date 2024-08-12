class Event:
    def __init__(self, id_ev="", title="", place="", descr="", dates="", im_url="", im_auth="", site_url="",
                 next_e="", categ=""):
        self.id_ev = id_ev
        self.title = title
        self.place = place
        self.descr = descr
        self.dates = dates
        self.im_url = im_url
        self.im_auth = im_auth
        self.site_url = site_url
        self.next_e = next_e
        self.categ = categ

    def reset(self):
        for attr in vars(self):
            setattr(self, attr, "")



