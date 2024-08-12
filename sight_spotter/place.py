class Place:
    def __init__(self, id_pla, name, dist, kinds,
                 wikidata="", im_url="", im_auth=""):
        self.id_pla = id_pla
        self.name = name
        self.dist = dist
        self.kinds = kinds
        self.wikidata = wikidata
        self.im_url = im_url
        self.im_auth = im_auth
