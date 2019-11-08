from json import dumps
from requests import get
from datetime import datetime
from bs4 import BeautifulSoup
from xlrd import open_workbook
from re import sub
import os
import json


url = "https://www.s-vfu.ru/universitet/rukovodstvo-i-struktura/instituty/imi/uchebnyy-protsess/"


class JsonHandler:

	def __init__(self):
		self.default = {"groups": [
				"ПИ-19-1", "ПИ-19-2",
				"ИВТ-19-1", "ИВТ-19-2", "ИВТ-19-3"
				], 
				"currentGroup": "ИВТ-19-3"
				}

		self.generateConfig()


	def read(self, field = None):
		with open("config.json", "r+", encoding="utf-8") as file:
			data = json.loads(file.read())

		if field is not None and field in data:
			return data[field]
		else:
			return data


	def write(self, field, value):
		data = self.read()

		if field in data:

			if "**default**" in value:
				data[field] = self.default[field]

			else:
				if isinstance(data[field], list):
					if isinstance(value, list):
						data[field] = value
					else:
						data[field].append(value)
				else:
					data[field] = value

			with open("config.json", "w", encoding="utf-8") as file:
				file.write(json.dumps(data, ensure_ascii=False, indent=4))


	def reset(self, field, value):
		data = self.read()

		if field in data:

			if "**default**" in value:
				with open("config_copy.json", "w", encoding="utf-8") as file:
					file.write(json.dumps(data, ensure_ascii=False, indent=4))

				data = self.default

			else:
				if isinstance(data[field], list):
					if isinstance(value, list):
						for value_ in value:
							if value_ in data[field]:
								data[field].remove(value_)
					else:
						if value in data[field]:
							data[field].remove(value)
				else:
					data[field] = value

			with open("config.json", "w", encoding="utf-8") as file:
				file.write(json.dumps(data, ensure_ascii=False, indent=4))


	def generateConfig(self):
		listDir = os.listdir(os.getcwd())

		if "config.json" not in listDir:	
			with open("config.json", "w", encoding="utf-8") as file:
				file.write(json.dumps(self.default, ensure_ascii=False, indent=4))


class Document:

	def __init__(self):
		self.url = url
		self.get_group()
		soup = self.open_soup()
		content = self.content_searcher(soup)
		print(content)
		self.file = self.get_document(content)

	def get_group(self):
		self.sheet_name = "1 курс_ИТ" # наименование рабочей страницы строго как в эксель файле
		self.group = config.read("currentGroup") # название рассматриваемой группы как в эксель файле(кол-во студентов указывать не нужно), однако капсом или нет - неважно
		self.column=14 # дефолт

	def open_soup(self):
		response = get(self.url).content
		soup = BeautifulSoup(response, 'lxml')
		return soup

	def content_searcher(self, soup):
		content = soup.find("div", id="content")
		for a in content.find_all("a"):
			print(a.text)
			if "Расписание ИМИ" in a.text:
				return "https://www.s-vfu.ru"+a.get('href')

	def get_document(self, url):
		r = get(url, stream=True)
		path = "table.xls"

		with open(path, "wb") as out:
			for chunk in r.iter_content(512):
				out.write(chunk)

		return path


class ParseDocument(Document):

	def __init__(self):
		super().__init__()
		sheet, week, date = self.open_excel()
		table = self.generateTable(sheet, week, date)
		self.file_input(table)


	def open_excel(self):
		now = datetime.now()
		date = now.strftime("%d-%m-%Y")
		week_dig = 1 + int(now.strftime("%U")) # порядковый номер недели для проверки четности
		week_t = None

		if week_dig % 2 == 0:
			week_t = "Четная"
		else:
			week_t = "Нечетная"

		rb = open_workbook(self.file, formatting_info=True)
		sheet = rb.sheet_by_name(self.sheet_name)

		for column in range(sheet.ncols):
			if self.group in sheet.cell_value(2, column).lower():
				self.column = column # запоминаем местоположение столбца нашей группы

		return sheet, week_t, date


	def generateTable(self, sheet, week, date):
		days = []
		d = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]
		tbl = {
			f'{date}. Неделя': f'{week}',
			'Расписание для': f'{self.sheet_name} {sheet.cell_value(2, self.column)}',
			'Понедельник': [],
			'Вторник': [],
			'Среда': [],
			'Четверг': [],
			'Пятница': [],
			'Суббота': []
		}

		for row in range(3, sheet.nrows):
			'''
			первая строка каждого нового дня содержит имя недели, а остальные строки - пусты
			например
			1 понедельник    матеша
			2                физра
			3                информатика
			4 вторник        химия
			5                биология
			...
			поэтому, итерируя каждую строку, мы прежде всего проверяем, не новый ли это день
			а если так, то запоминаем его
			'''

			if len(sheet.cell_value(row, 0)):
				for item in d:
					if item in sheet.cell_value(row, 0).lower():
						days.append(item)

			time = sheet.cell_value(row, 1).strip().replace("--", "-") # время
			subject = sheet.cell_value(row, self.column) # предмет
			kind = sheet.cell_value(row, self.column+1 ) # тип занятия(лек., пр., лаб.)
			audience = "" # аудитория

			for i in range(2, self.column-1): # ищем номер аудитории
				p = sheet.cell_value(row, self.column+i)

				if isinstance(p, float):
					audience = str(p).split(".")[0]
					break
				elif "".join(str(p).split(" ")).isdigit():
					audience = p
					break
				elif not "".join(str(p).split(" ")).isdigit():
					continue

			if not(len(subject)):
				'''
				иногда предмет охватывает несколько ячеек и его названия нет в колонке column
				тут мы вроде ищем его название в соседних ячейках, хотя я сам забыл уже и вообще спать хочу
				'''
				if len(sheet.cell_value(row, self.column+1)):
					for i in range(1, sheet.ncols):
						if len(sheet.cell_value(row, self.column-i)):
							subject = sheet.cell_value(row, self.column-i)
							break

				elif not any(_.split('.')[0].isdigit() for _ in str(sheet.cell_value(row, self.column-1)).split(" ")):
					for i in range(1, self.column-1):
						iCell = sheet.cell_value(row, self.column-i) 

						if not isinstance(iCell, float):
							if not "".join(str(iCell).split(" ")).isdigit():
								if len(iCell):
									subject = iCell
									break
							else:
								break
						else:
							break

			subject = sub(r' +', ' ', str(subject)).strip().replace("\n", " ") # убираем дебильные пробелы
			audience = sub(r' +', ' ', str(audience)).strip().replace("\n", " ")

			if subject == "":
				tbl[days[-1].title()].append(f"{time} -" if len(time) else "-")
				continue

			elif "физич" in ''.join(subject.lower().split(' ')): # заменяем Ф И З И Ч Е С К А Я... на нормальное написание
				subject = "Физ. культура"
				tbl[days[-1].title()].append(f"{time} {subject}")
				continue

			elif "исто" in ''.join(subject.lower().split(' ')):
				if "яковлев" in subject.lower():
					subject = "История Яковлел А.И."

			elif "дв2" in subject.lower():
				subject = "Якутский язык"

			elif any(_ in subject.lower() for _ in ['дв', 'культура']):
				subject = "Культура и традиции"

			tbl[days[-1].title()].append(f"{time} {subject}   Ауд. {audience} {kind}")

		return tbl


	def file_input(self, table):
		with open("table.txt", "w", encoding='utf-8') as file:
			for j, (k, v) in enumerate(table.items()):
				if j > 1:
					file.write(f"{k}:\n")	
					for i, item in enumerate(v):
						if i == len(v)-1:
							file.write(f"\t{item}\n\n")
						else:
							file.write(f"\t{item}\n")
				elif j == 0:
					file.write(f"{k}: {v}\n")
				elif j == 1:
					file.write(f"{k}: {v.replace('_', ' ')}\n\n")
				j+=1

		with open("table.json", "w", encoding="utf-8") as file:
			file.write(dumps(table, ensure_ascii=False, indent=4))



if __name__ == '__main__':
	config = JsonHandler()
	ParseDocument()