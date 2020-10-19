import bs4 as bs
import requests
from urllib.parse import quote


'''
скрипт для формирования базы институтов
запускается вручную
выхлоп нужно поместить в переменную database библиотеки JsonHandler
можно подкрутить к приложению, но формируется слишком долго
'''


def get_institutes():
	'''
	простой скрипт для получения списка институтов
	'''

	headers = {
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
		"Accept-Encoding": "gzip, deflate, br",
		"Accept-Language": "ru,en;q=0.9",
		"Connection": "keep-alive",
		"Host": "www.s-vfu.ru",
		"Referer": "https://www.google.ru/",
		"Sec-Fetch-Mode": "navigate",
		"Sec-Fetch-Site": "same-origin",
		"Sec-Fetch-User": "?1",
		"Upgrade-Insecure-Requests": "1",
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 YaBrowser/19.12.0.358 Yowser/2.5 Safari/537.36"
	}

	request = requests.get(url='https://www.s-vfu.ru/raspisanie/', headers=headers).content
	soup = bs.BeautifulSoup(request, "html.parser")

	select = []

	for a in soup.find_all("option"):
		if len(a.attrs['value']):
			select.append(a.attrs['value'])

	return select


def get_groups(date, is_main = False):
	'''
	скрипт посложнее для получения списка курсов каждого института, а также списка групп каждого курса
	'''

	institutes = get_institutes()

	headers = {
		"Host": "www.s-vfu.ru",
		"Connection": "keep-alive",
		"Content-Length": "58",
		"Accept": "*/*",
		"Origin": "https://www.s-vfu.ru",
		"X-Requested-With": "XMLHttpRequest",
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.136 YaBrowser/20.2.2.177 Yowser/2.5 Safari/537.36",
		"DNT": "1",
		"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
		"Sec-Fetch-Site": "same-origin",
		"Sec-Fetch-Mode": "cors",
		"Referer": "https://www.s-vfu.ru/raspisanie/",
		"Accept-Encoding": "gzip, deflate, br",
		"Accept-Language": "ru,en;q=0.9",
	}

	data = {}
	soup_data = []

	for inst in institutes:
		u = f"action=showgroups&fac={quote(inst)}&mydate={date}" # для каждого института формируется отдельный запрос на список курсов и групп

		request = requests.post(url='https://www.s-vfu.ru/raspisanie/ajax.php', headers=headers, data=u).content
		soup = bs.BeautifulSoup(request, "html.parser")


		if is_main:
			soup_data.append(f"{inst}\t{soup}\n\n")


		# находим тег<select class="firsted" ... </select>
		# он содержит в себе первым элементом <option selected="selected" value="">Выберите вашу группу</option>, который мы отсеиваем при дальнейшей итерации
		# вторым элементом идет optgroup, который закрывается только в самом конце, а значит парсить в цикле будем его, т.к он содержит в себе все элементы
		main_tag = soup.find_all()[0].find_all()


		if len(main_tag) < 2: # проверяем, не пуст ли селектор групп
			continue

		data[inst] = {}


		# bs съедать первый первый optgroup, скорее всего содержащий текст "очная, 1 курс (Бакалавриат)", но это может быть не точно,
		# поэтому находим его вручную, чтоб совесть была чиста
		tag = main_tag[1].attrs['label'].split(', ')[1] 


		data[inst][tag] = []

		for item in main_tag[1].find_all():
			if item.name == "optgroup":
				tag = item.attrs['label'].split(', ')[1]
				data[inst][tag] = []
				continue

			data[inst][tag].append(item.text)

	if is_main:
		with open("test.html", "r+", encoding="utf-8") as file:
			# f = open("test.html", "r+")
			# f.writelines()
			file.writelines(soup_data)

	sorting(data)
	return data


def sorting(data):
	'''
	TODO: сортировка по курсам: 1, 2, 3 (Бакалавриат), 1, 2, 3 (Магистры), 1, 2, 3 (Послевуз)
	1 (Бакалавриат), 1 (Магистры), 1 (Послевуз), 2 (Бакалавриат) и тд.
	'''

	pass


if __name__ == '__main__':
	from datetime import datetime
	import json

	now = datetime.now()
	date = now.strftime("%d-%m-%Y")
	open("test.html", "w")

	data = get_groups(date, True)

	# f = open("test.json", "w+", encoding='utf-8')
	# print(data == json.loads(f.read()))

	with open("test.json", "w", encoding='utf-8') as file:
		file.write(json.dumps(data, ensure_ascii=False, indent=4))