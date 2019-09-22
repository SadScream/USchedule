import re
import json
import requests
import bs4 as bs
import xlrd


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
		rb = xlrd.open_workbook(self.file, formatting_info=True)
		sheet_name = "1 курс_ИТ"
		sheet = rb.sheet_by_name(sheet_name)
		column=14 # дефолтный номер колонны(ивт-19-3) для случая, если будет неправлено указана группа
		table = []

		for col in range(sheet.ncols):
			if "ивт-19-3" in sheet.cell_value(2,col).lower():
				column = col # запоминаем местоположение столбца нашей группы

		days = []
		d = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]
		tbl = {'Расписание для': f'{sheet_name} {sheet.cell_value(2,column)}', 'Понедельник': [], 'Вторник': [], 'Среда': [], 'Четверг': [], 'Пятница': [], 'Суббота': []}

		for row in range(3,sheet.nrows):
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
				if sheet.cell_value(row,0).lower() in d:
					days.append(sheet.cell_value(row,0).lower())

			t = sheet.cell_value(row,1).strip() # время
			v = sheet.cell_value(row,column) # предмет
			f = sheet.cell_value(row,column+1 ) # тип занятия(лек., пр., лаб.)
			k = "" # аудитория

			for i in range(2, column-1): # ищем номер аудитории
				p = sheet.cell_value(row,column+i)

				if isinstance(p, float):
					k = str(p).split(".")[0]
					break
				elif "".join(str(p).split(" ")).isdigit():
					k = p
					break
				elif not "".join(str(p).split(" ")).isdigit():
					continue


			if not(len(v)):
				'''
				иногда предмет охватывает несколько ячеек и его названия нет в колонке column
				тут мы вроде ищем его название, хотя я сам забыл уже и вообще спать хочу
				'''
				if len(sheet.cell_value(row,column+1)):
					for i in range(1, sheet.ncols):
						if len(sheet.cell_value(row,column-i)):
							v = sheet.cell_value(row,column-i)
							break

				elif not isinstance(sheet.cell_value(row,column-1), float):
					for i in range(1, column-1):
						if not isinstance(sheet.cell_value(row,column-i), float):
							if not "".join(str(sheet.cell_value(row,column-i)).split(" ")).isdigit():
								if len(sheet.cell_value(row,column-i)):
									v = sheet.cell_value(row,column-i)
									break
							else:
								break
						else:
							break

			v = re.sub(r' +', ' ', str(v)).strip().replace("\n", " ") # убираем дебильные пробелы
			k = re.sub(r' +', ' ', str(k)).strip().replace("\n", " ")

			if v == "":
				tbl[days[-1].title()].append(f"{t} -" if len(t) else "-")
				continue
			elif "ф и з и ч" in v.lower(): # заменяем Ф И З И Ч Е С К А Я... на нормальное написание
				v = "Физ. культура"
				tbl[days[-1].title()].append(f"{t} {v}")
				continue
			elif "и с т о" in v.lower():
				if "яковлев" in v.lower():
					v = "История Яковлел А.И."
					tbl[days[-1].title()].append(f"{t} {v}   Ауд. {k} {f}")
					continue

			tbl[days[-1].title()].append(f"{t} {v}   Ауд. {k} {f}")

		with open("table.txt", "w", encoding='utf-8') as file:
			for k, v in tbl.items():
				if "Расписание" in k:
					file.write(f"Расписание для: {v}\n\n")
					break

			for k, v in tbl.items():
				if "Расписание" not in k:
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