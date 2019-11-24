# -*- coding: utf-8 -*-

from json import dumps
from requests import get
from datetime import datetime
from bs4 import BeautifulSoup
from xlrd import open_workbook
from re import sub, findall
from JsonHandler import JsonHandler
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

		self.sheet_name = config.read("currentCourse") # наименование рабочей страницы строго как в эксель файле
		self.group = config.read("currentGroup") # название рассматриваемой группы как в эксель файле(кол-во студентов указывать не нужно), однако капсом или нет - неважно
		self.last_column = 0
		self.first_row = 0

		now = datetime.now()
		date = now.strftime("%d-%m-%Y")
		week = "Четная" if (1 + int(now.strftime("%U"))) % 2 == 0 else "Нечетная"

		sheet = self.open()
		table = self.generateTable(sheet, week, date)

		self.file_input(table)

	def open(self):
		rb = open_workbook(self.file, formatting_info=True)
		sheet = rb.sheet_by_name(self.sheet_name)

		for row in range(sheet.nrows): # находим номера первого ряда(ячейка "день") и последнего(суббота)
			if "понедельник" in sheet.cell_value(row, 0).lower():
				self.first_row = row-1
			if "суббота" in sheet.cell_value(row, 0).lower():
				self.last_row = row+6
				break

		found = False
		for column in range(sheet.ncols):
			if self.group.lower() in str(sheet.cell_value(self.first_row, column)).lower():
				self.column = column # запоминаем местоположение столбца нашей группы
			else:
				for i in range(5):
					if "недели" in str(sheet.cell_value(self.first_row-2+i, column)).lower(): # номер последней колонны
						self.last_column = column
						found = True
						break
				if found:
					break

		return sheet

	def generateTable(self, sheet, week, date):
		days = []
		DAYS = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]

		self.tbl = {
			f'{date}. Неделя': f'{week}',
			'Расписание для': f'{self.sheet_name} {sheet.cell_value(self.first_row, self.column)}',
			'Понедельник': [],
			'Вторник': [],
			'Среда': [],
			'Четверг': [],
			'Пятница': [],
			'Суббота': []
		}

		for row in range(self.first_row+1, self.last_row):
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
				for item in DAYS:
					if item in sheet.cell_value(row, 0).lower():
						days.append(item)

			time = sheet.cell_value(row, 1).strip().replace("--", "-") # время
			subject = sheet.cell_value(row, self.column) # предмет
			kind = sheet.cell_value(row, self.column+1) # тип занятия(лек., пр., лаб.)
			audience = "" # аудитория

			if not(len(subject)):
				'''
				иногда предмет охватывает несколько ячеек и его названия нет в колонке column
				тут мы ищем его название в соседних ячейках
				'''

				if len(sheet.cell_value(row, self.column+1)):
					for i in range(1, sheet.ncols):
						if len(sheet.cell_value(row, self.column-i)):
							subject = sheet.cell_value(row, self.column-i)
							break

				else:
					for i in range(1, self.column-1):
						cellValue = str(sheet.cell_value(self.first_row, self.column-i)).lower()
						iCell = str(sheet.cell_value(row, self.column-i)) 

						if "".join(cellValue.split(" ")) in ["", "ауд"]:
							if len("".join(iCell.split(" "))) > 2:
								break
							continue

						if "студентов" not in cellValue:
							continue

						if not "".join(iCell.lower().split(" ")) in ["", "."] and len(iCell) > 2:
							subject = iCell
							break

			if not(len(kind)):
				for i in range(1, self.last_column-self.column):
					cellValue = str(sheet.cell_value(self.first_row, self.column+i)).lower()
					iCell = str(sheet.cell_value(row, self.column+i))

					if "".join(cellValue.split(" ")) in ["", "ауд"] or "студентов" in cellValue:
						if len("".join(iCell.split(" "))) > 2:
							break
						continue

					if len(iCell) == 0:
						continue

					kind = iCell
					break

			for i in range(2, self.last_column-self.column): # ищем номер аудитории
				cellValue = str(sheet.cell_value(self.first_row, self.column+i)).lower()

				if "".join(cellValue.split(" ")) not in ["", "ауд"]:
					continue

				p = sheet.cell_value(row, self.column+i)

				if not(len(str(p))):
					continue
				elif isinstance(p, float):
					p = int(p)

				audience = p
				break

			subject = sub(r' +', ' ', str(subject)).strip().replace("\n", " ") # убираем дебильные пробелы
			audience = sub(r' +', ' ', str(audience)).strip().replace("\n", " ")

			if subject == "":
				if len(self.tbl[days[-1].title()]) != 6:
					self.tbl[days[-1].title()].append(f"{time}: -" if len(time) else "-")
				continue

			elif "физич" in ''.join(subject.lower().split(' ')): # заменяем Ф И З И Ч Е С К А Я... на нормальное написание
				subject = "Физ. культура"
				self.tbl[days[-1].title()].append(f"{time}: {subject}")
				continue

			elif "исто" in ''.join(subject.lower().split(' ')):
				addiction = ""

				if "**" in subject:
					addiction = "**"
				elif "*" in subject:
					addiction = "*"

				if "яковлев" in subject.lower():
					subject = f"История{addiction} Яковлел А.И."

			elif all(_ in subject.lower() for _ in ['дв2', 'якут']):
				subject = "Якутский язык"

			elif all(_ in subject.lower() for _ in ['дв', 'культура']):
				subject = "Культура и традиции"

			self.tbl[days[-1].title()].append(f"{time}: {subject}   Ауд. {audience} {kind}")

		return self.tbl


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