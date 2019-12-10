# -*- coding: utf-8 -*-

from os import listdir, getcwd
from json import loads, dumps


class JsonHandler:

	def __init__(self):
		self.default = {
					"courses": [
						{"1 курс_ИТ": [
							"ПИ-19-1",
							"ПИ-19-2",
							"ИВТ-19-1",
							"ИВТ-19-2",
							"ИВТ-19-3",
							"ИТСС-19"
							]},
						{"1 курс_МО": [
							"БА-М-19",
							"МПО-19",
							"ПОИМ-19",
							"ПМИ-19-1",
							"ПМИ-19-2 ",
							"ФИИТ-19"
						]},
						{"2 курс _ИТ": [
							"ПИ-18-1",
							"ПИ-18-2",
							"ФИИТ-18",
							"ИВТ-18",
							"ИВТПО-18",
							"ИТСС-18"
						]},
						{"2 курс_МО": [
							"БА-М-18",
							"МПО-18",
							"ПОИМ-18",
							"ПМИ-18-1",
							"ПМИ-18-2"
						]},
						{"3 курс_ИТ": [
							"БА-ПИ-17-1",
							"БА-ПИ-17-2",
							"БА-ФИИТ-17",
							"ИВТ-17",
							"ИТСС-17-1",
							"ИТСС-17-2",
							"ИВТПО-17"
						]},
						{"3 курс_МО": [
							"БА-МО-17",
							"МПО-17-1",
							"МПО-17-2",
							"ИНФ-17",
							"ПМИ-17"
						]},
						{"4 курс_ИТ": [
							"БА-ПИ-16-1",
							"БА-ПИ-16-2",
							"ФИИТ-16",
							"ИВТ-16",
							"МТС-16",
							"МТС-16 уск",
							"ССиСК-16",
							"ИВТПО-16"
						]},
						{"4 курс_МО": [
							"БА-МО-16",
							"МПО-16",
							"ИНФ-16",
							"ПМ-16"
						]}
					],
					"fonts": ["11 шрифт", "13 шрифт", "15 шрифт", "17 шрифт", "19 шрифт", "21 шрифт", "23 шрифт", "25 шрифт", "27 шрифт"],
					"currentCourse": "",
					"currentGroup": "",
					"currentFont": "15 шрифт",
					"lastSchedule": "",
					"schedule": "",
					"groupJson": ""
				}
		self.generateConfig()


	def read(self, field = None):
		with open("config.json", "r+", encoding="utf-8") as file:
			data = loads(file.read())

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
				file.write(dumps(data, ensure_ascii=False, indent=4))


	def reset(self, field, value):
		data = self.read()

		if field in data:

			if "**default**" in value:
				with open("config_copy.json", "w", encoding="utf-8") as file:
					try:
						file.write(dumps(data, ensure_ascii=False, indent=4))
					except:
						file.write(dumps(self.default, ensure_ascii=False, indent=4))

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
				try:
					file.write(dumps(data, ensure_ascii=False, indent=4))
				except:
					file.write(dumps(self.default, ensure_ascii=False, indent=4))


	def generateConfig(self):
		listDir = listdir(getcwd())

		if "config.json" not in listDir:	
			with open("config.json", "w", encoding="utf-8") as file:
				file.write(dumps(self.default, ensure_ascii=False, indent=4))

		elif "config.json" in listDir:
			data = self.read()

			for k, v in self.default.items():
				if k not in data:
					with open("config.json", "w", encoding="utf-8") as file:
						file.write(dumps(self.default, ensure_ascii=False, indent=4))
						return