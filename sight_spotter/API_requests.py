import requests
from OSMPythonTools.nominatim import Nominatim
nominatim = Nominatim()


headers = {'User-Agent': 'bot'}
API_KEY = ""


def get_city_inf(city):
    city_inf = requests.get(f'http://api.opentripmap.com/0.1/ru/places/geoname?lang=ru&name={city}&apikey={API_KEY}')
    return city_inf.json()


def get_addr_inf(city, addr):
    return nominatim.query(f'{city}, {addr}', headers=headers).toJSON()[0]


def get_place_inf(rad, lon, lat, kinds=""):
    if kinds != "":
        place_inf = requests.get(
            f'https://api.opentripmap.com/0.1/ru/places/radius?radius={rad}&lon={lon}&lat={lat}&kinds={kinds}&rate=1&apikey={API_KEY}')
    else:
        place_inf = requests.get(
            f'https://api.opentripmap.com/0.1/ru/places/radius?radius={rad}&lon={lon}&lat={lat}&rate=1&apikey={API_KEY}')
    return place_inf.json()


def get_im_info(wiki_id):
    im_wiki = requests.get(f"https://www.wikidata.org/w/api.php?action=wbgetclaims&entity="
                           f"{wiki_id}&property=P18", headers=headers)
    return im_wiki.text


def get_im_auth(filename):
    im_wiki_inf = requests.get(
                    f'https://commons.wikimedia.org/w/api.php?action=query&titles=Image:{filename}&prop=imageinfo&format=json', headers=headers)
    return im_wiki_inf.text


def get_event_inf(since, till, categ, lon, lat, rad):
    event_inf = requests.get(
        f'https://kudago.com/public-api/v1.4/events/?lang=ru&page=1&page_size=1&fields=id,title,description,place,dates,'
        f'images,categories,site_url&text_format=text&actual_since={since}&actual_until={till}&categories={categ}'
        f'&lon={lon}&lat={lat}&radius={rad}')
    return event_inf.json()


def get_event_place_name(place_id):
    answer = requests.get(f"https://kudago.com/public-api/v1.4/places/{place_id}/")
    return answer.json()
