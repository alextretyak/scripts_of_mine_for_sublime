if __name__ != "__main__":
	raise BaseException

import ctypes, urllib, requests, sys, os
import logging

# https://stackoverflow.com/questions/10588644/how-can-i-see-the-entire-http-request-thats-being-sent-by-my-python-application/10588737
import http.client as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

MessageBox = ctypes.windll.user32.MessageBoxW # https://stackoverflow.com/a/4485736/2692494

fname = sys.argv[3]
if not os.path.isfile(fname):
	try:
		r = requests.get(("https://www.google.ru/search?num=20&q=" if sys.argv[1] == "GOOGLE" else
		                  "https://yandex.ru/search/?text=") + urllib.parse.quote_plus(sys.argv[2]),
		headers={'user-agent': 'Lynx/2.9.2 libwww-FM/2.14 SSL-MM/1.4.1 OpenSSL/3.4.0'} # [https://github.com/benbusby/whoogle-search/commit/6f1e1e6847640c611e9fe21e123d4f63e4c56aa6 <- https://github.com/benbusby/whoogle-search/issues/1211 <- google:‘requests "If you're having trouble accessing Google Search"’]
		    if sys.argv[1] == "GOOGLE" else # при user-agent по умолчанию (python-requests/2.10.0) почему-то возвращается страница в кодировке cp1251 (зато размер 50Кб, а так 86Кб {но с ...Chrome... user-agent вообще 293Кб})
			{'User-Agent': 'Opera/9.80 (Windows NT 6.2; WOW64) Presto/2.12.388 Version/12.16',
			'Accept': 'text/html, application/xml;q=0.9, application/xhtml+xml, image/png, image/webp, image/jpeg, image/gif, image/x-xbitmap, */*;q=0.1',
			'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
			'Cookie': 'yandexuid=2757746121481971382; _ym_uid=1481971392244882530; fuid01=54a22b7364cb7f91.bNwIDwRDKMMJTygAi3cSVRmllhnq0zMTdP3xFsL977-CN0q71HjJ2KW8uWQSN4zV-TgAvxqYcyUTaFmLyPH2AGDLdpdNoqz4O8Y_DCtHfumOPS91CqmRIOAXI3PTVQM2; mda=0; yabs-frequency=/4/0000000000000000/UagmSDGg87nAi73KAY40/; i=nTKaCGz7craV+EnEBbai1hptjl3uoPJ8R0JmctVjVtN6o3cM6nPfGB1rgOutqgWPOdc66PRXBX638HGsTXyuiKWYjMg=; _ym_isad=2; ys=wprid.1507377172842348-1376652669972222364414631-vla1-3015; yp=1516723027.szm.1%3A1920x1080%3A1920x957#1538913166.wzrd_sw.1507377166#1538913167.dsws.1#1538913167.dswa.0#1538913167.dwbrowsers.1#1507463567.ln_tp.01#1538913177.p_sw.1507377176'
			}
		)
		r.raise_for_status()
		open(fname, "w", encoding='utf-8').write(r.text)
	except:
		MessageBox(None, sys.argv[2], 'HTTP Error', 0)
		exit(1)
	print(r.headers)
