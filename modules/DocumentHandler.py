# -*- coding: utf-8 -*-

from json import dumps
from requests import get
from datetime import datetime
from bs4 import BeautifulSoup
from xlrd import open_workbook
from re import sub
from .JsonHandler import JsonHandler
import os


url = "https://www.s-vfu.ru/universitet/rukovodstvo-i-struktura/instituty/imi/uchebnyy-protsess/"
config = JsonHandler()


class Parser:

	def __init__(self):
		self.url = url
		self.content = self.getContentLink()
		self.updated = False

		if self.content == False:
			self.updated = True
			self.file = os.path.join(os.getcwd(), "table.xls" if "table.xls" in os.listdir() else "table.xlsx")
		else:
			self.file = self.getContent(self.content)


	def getContentLink(self):
		response = get(self.url).content
		soup = BeautifulSoup(response, 'lxml')
		link = ""

		content = soup.find("div", id="content")
		for a in content.find_all("a"):
			if "Расписание ИМИ" in a.text:
				link = "https://www.s-vfu.ru"+a.get('href')

				if config.read("lastSchedule") == link:
					if "table.xls" in os.listdir() or "table.xlsx" in os.listdir():
						return False

				config.write("lastSchedule", link)
				return link


	def getContent(self, url):
		r = get(url, stream=True)
		path = "table.xls"

		with open(path, "wb") as out:
			for chunk in r.iter_content(512):
				out.write(chunk)

		return path


class Document(Parser):

	def __init__(self):
		super().__init__()
		self.get_data()

		now = datetime.now()
		date = now.strftime("%d-%m-%Y")
		week_dig = 1+int(now.strftime("%U")) # порядковый номер недели для проверки четности

		if week_dig % 2 == 0:
			week = "Четная"
		else:
			week = "Нечетная"

		sheet = self.open()
		table = self.generateTable(sheet, week, date)
		self.file_input(table)


	def get_data(self):
		self.sheet_name = config.read("currentSheet") # наименование рабочей страницы строго как в эксель файле
		self.group = config.read("currentGroup") # название рассматриваемой группы как в эксель файле(кол-во студентов указывать не нужно), однако капсом или нет - неважно
		self.column=14 # дефолт


	def open(self):
		rb = open_workbook(self.file, formatting_info=True)
		sheet = rb.sheet_by_name(self.sheet_name)

		for column in range(sheet.ncols):
			if self.group.lower() in sheet.cell_value(2, column).lower():
				self.column = column # запоминаем местоположение столбца нашей группы

		return sheet


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
		# with open("table.txt", "w", encoding='utf-8') as file:
		# 	for j, (k, v) in enumerate(table.items()):
		# 		if j > 1:
		# 			file.write(f"{k}:\n")	
		# 			for i, item in enumerate(v):
		# 				if i == len(v)-1:
		# 					file.write(f"\t{item}\n\n")
		# 				else:
		# 					file.write(f"\t{item}\n")
		# 		elif j == 0:
		# 			file.write(f"{k}: {v}\n")
		# 		elif j == 1:
		# 			file.write(f"{k}: {v.replace('_', ' ')}\n\n")
		# 		j+=1

		with open("table.json", "w", encoding="utf-8") as file:
			file.write(dumps(table, ensure_ascii=False, indent=4))



if __name__ == '__main__':
	Document()