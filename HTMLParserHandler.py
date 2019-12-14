import bs4 as bs
import requests
from urllib.parse import quote


'''
файл для формирования базы институтов
запускается вручную
выхлоп нужно поместить в переменную database библиотеки JsonHandler
можно подкрутить к приложению, но формируется слишком долго, надо думать
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

	for a in soup.find_all("li"):
		select.append(a.text)

	return select


def get_groups(date):
	'''
	скрипт посложнее для получения списка курсов каждого института, а также списка групп каждого курса
	'''

	institutes = get_institutes()

	headers = {
		"Accept": "*/*",
		"Accept-Encoding": "gzip, deflate, br",
		'Accept-Language': "ru,en;q=0.9",
		"Connection": "keep-alive",
		"Content-Length": "58",
		"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
		"Host": "www.s-vfu.ru",
		"Origin": "https://www.s-vfu.ru",
		'Referer': "https://www.s-vfu.ru/raspisanie/",
		"Sec-Fetch-Mode": "cors",
		"Sec-Fetch-Site": 'same-origin',
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 YaBrowser/19.12.0.358 Yowser/2.5 Safari/537.36",
		"X-Requested-With": "XMLHttpRequest"
	}

	data = {}

	for inst in institutes:
		u = f"action=showgroups&fac={quote(inst)}&mydate={date}" # для каждого института формируется отдельный запрос на список курсов и групп
		data[inst] = []

		request = requests.post(url='https://www.s-vfu.ru/raspisanie/ajax.php', headers=headers, data=u).content
		soup = bs.BeautifulSoup(request, "html.parser")

		for i, ort_group in enumerate(soup.find_all("optgroup")): # ortgroup - курсы
			ort_splited = ort_group.attrs['label'].split(', ')[1] # убираем лишнюю часть из наименования курса

			data[inst].append({ort_splited: []})

			for j, group in enumerate(ort_group.find_all("option")): # option - группы

				if len(data[inst]):
					'''
					далее проверка, на случай, если в списке групп какого-то курса уместились все группы последующих курсов
					случается из-за незакрытого тега
					'''

					for k, v in data[inst][i-1].items():
						if group.text in v:
							key = [_ for _ in data[inst][i-1]][0]

							for n, item in enumerate(v):
								if item == group.text:
									data[inst][i-1][key] = data[inst][i-1][key][:n]
									break

				data[inst][i][ort_splited].append(group.text)

	return data


if __name__ == '__main__':
	from datetime import datetime
	import json

	now = datetime.now()
	date = now.strftime("%d-%m-%Y")
	data = get_groups(date)

	f = open("test.json", "r", encoding='utf-8')
	print(data == json.loads(f.read()))

	with open("test.json", "w", encoding='utf-8') as file:
		file.write(json.dumps(data, ensure_ascii=False, indent=4))