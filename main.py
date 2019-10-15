import re
import json
import requests
import bs4 as bs
import xlrd
import datetime


url = "https://www.s-vfu.ru/universitet/rukovodstvo-i-struktura/instituty/imi/uchebnyy-protsess/"


class Document:

	def __init__(self):
		self.url = url
		soup = self.open_soup()
		content = self.content_searcher(soup)
		print(content)
		self.file = self.get_document(content)

	def open_soup(self):
		response = requests.get(self.url).content
		soup = bs.BeautifulSoup(response, 'lxml')
		return soup

	def content_searcher(self, soup):
		content = soup.find("div", id="content")
		for a in content.find_all("a"):
			print(a.text)
			if "Расписание ИМИ" in a.text:
				return "https://www.s-vfu.ru"+a.get('href')

	def get_document(self, url):
		r = requests.get(url, stream=True)
		path = "table.xls"

		with open(path, "wb") as out:
			for chunk in r.iter_content(512):
				out.write(chunk)

		return path


class ParseDocument(Document):

	def __init__(self):
		super().__init__()
		self.open_excel()

	def open_excel(self):
		now = datetime.datetime.now()
		date = now.strftime("%d-%m-%Y")
		week_dig = 1+int(now.strftime("%U")) # порядковый номер недели для проверки четности
		week_t = None

		if week_dig % 2 == 0:
			week_t = "Четная"
		else:
			week_t = "Нечетная"

		sheet_name = "1 курс_ИТ" # наименование рабочей страницы строго как в эксель файле
		group = "ивт-19-3" # название рассматриваемой группы как в эксель файле(кол-во студентов указывать не нужно), однако капсом или нет - неважно
		column=14 # дефолт

		rb = xlrd.open_workbook(self.file, formatting_info=True)
		sheet = rb.sheet_by_name(sheet_name)
		table = []

		for col in range(sheet.ncols):
			if group in sheet.cell_value(2,col).lower():
				column = col # запоминаем местоположение столбца нашей группы

		days = []
		d = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]
		tbl = {
			f'{date}. Неделя': f'{week_t}',
			'Расписание для': f'{sheet_name} {sheet.cell_value(2,column)}',
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

			if len(sheet.cell_value(row,0)):
				for item in d:
					if item in sheet.cell_value(row,0).lower():
						days.append(item)

			time = sheet.cell_value(row,1).strip().replace("--", "-") # время
			subject = sheet.cell_value(row,column) # предмет
			kind = sheet.cell_value(row,column+1 ) # тип занятия(лек., пр., лаб.)
			audience = "" # аудитория

			for i in range(2, column-1): # ищем номер аудитории
				p = sheet.cell_value(row,column+i)

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
				тут мы вроде ищем его название, хотя я сам забыл уже и вообще спать хочу
				'''
				if len(sheet.cell_value(row,column+1)):
					for i in range(1, sheet.ncols):
						if len(sheet.cell_value(row,column-i)):
							subject = sheet.cell_value(row,column-i)
							break

				elif not any(_.split('.')[0].isdigit() for _ in str(sheet.cell_value(row,column-1)).split(" ")):
					for i in range(1, column-1):
						iCell = sheet.cell_value(row,column-i) 

						if not isinstance(iCell, float):
							if not "".join(str(iCell).split(" ")).isdigit():
								if len(iCell):
									subject = iCell
									break
							else:
								break
						else:
							break

			subject = re.sub(r' +', ' ', str(subject)).strip().replace("\n", " ") # убираем дебильные пробелы
			audience = re.sub(r' +', ' ', str(audience)).strip().replace("\n", " ")

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
					tbl[days[-1].title()].append(f"{time} {subject}   Ауд. {audience} {kind}")
					continue

			tbl[days[-1].title()].append(f"{time} {subject}   Ауд. {audience} {kind}")

		with open("table.txt", "w", encoding='utf-8') as file:
			for k, v in tbl.items():
				if any(_ in k for _ in ["Расписание", "Неделя"]):
					file.write(f"{audience}: {subject}\n\n")

				else:
					file.write(f"{k}:\n")	
					for i, item in enumerate(v):
						if i == len(v)-1:
							file.write(f"\t{item}\n\n")
						else:
							file.write(f"\t{item}\n")

		with open("table.json", "w+", encoding="utf-8") as file:
			file.write(json.dumps(tbl, ensure_ascii=False, indent=4))



if __name__ == '__main__':
	ParseDocument()