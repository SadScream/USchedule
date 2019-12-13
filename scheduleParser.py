import bs4 as bs
import requests
from urllib.parse import quote


class Document:

	def __init__(self, group, date):
		self.group = group
		self.date = date


	def complete(self):
		soup = self.get_soup()

		rasp = []

		for sym in str(soup):
			if sym != "<":
				rasp.append(sym)
			else:
				break

		Header = ''.join(rasp).replace('  ', ' ')

		data = {'DAT': Header}
		body = soup.find_all("tbody")[0]
		current_day = ''
		current_time = ''

		for line in body.find_all("tr"):
			if line.attrs["class"][0] == "error":
				current_day = line.text.split(" ")[0].capitalize()
				data[current_day] = {"08:00 - 09:35": [], "09:50 - 11:25": [], "11:40 - 13:15": [], "14:00 - 15:35": [], "15:50 - 17:25": [], "17:30 - 19:15": []}

			elif line.attrs["class"][0] == "success":
				for sub in line.find_all("td"):
					if sub.text.replace("-", " - ") in data[current_day]:
						current_time = sub.text.replace("-", " - ")
						continue
					data[current_day][current_time].append(sub.text.strip())

		data = self.reconstruct(data)

		return data


	def reconstruct(self, DATA):
		data = {}
		
		for k, v in DATA.items():
			if isinstance(v, dict):
				data[k] = {}

				for key, value in v.items():
					data[k][key] = ''

					for i, item in enumerate(value):

						if i % 2 == 0:
							if item not in data[k][key]:
								data[k][key] = data[k][key] + ' ' + item

						elif "подгруппа" in item.lower():
							a = "Подгруппа" + item.lower().split("подгруппа")[-1]
							data[k][key] = data[k][key] + ' ' + a
			else:
				data[k] = v

		return data


	def get_soup(self):
		headers = {
			"Host": "www.s-vfu.ru",
			"Connection": "keep-alive",
			"Content-Length": "99",
			"Accept": "*/*",
			"Origin": "https://www.s-vfu.ru",
			"X-Requested-With": "XMLHttpRequest",
			"Save-Data": "on",
			"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 YaBrowser/19.12.0.358 Yowser/2.5 Safari/537.36",
			"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
			"Sec-Fetch-Site": "same-origin",
			"Sec-Fetch-Mode": "cors",
			"Referer": "https://www.s-vfu.ru/raspisanie/",
			"Accept-Encoding": "gzip, deflate, br",
			"Accept-Language": "ru,en;q=0.9"
		}


		data = f"action=showrasp&groupname={quote(self.group)}&mydate={self.date}"
		request = requests.post(url='https://www.s-vfu.ru/raspisanie/ajax.php', headers=headers, data=data).content
		soup = bs.BeautifulSoup(request, "html.parser")

		return soup


if __name__ == '__main__':
	from datetime import datetime
	import json

	group = "ИМИ-БА-ИВТ-19-1"
	date = datetime.now().strftime("%d-%m-%Y")
	doc = Document(group, date).complete()
	
	with open("test.json", "w", encoding="utf-8") as file:
		file.write(json.dumps(doc, ensure_ascii=False, indent=4))