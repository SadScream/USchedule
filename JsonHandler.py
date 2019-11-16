from os import listdir, getcwd
from json import loads, dumps


default = {
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
		]}
	],
	"fonts": ["13 шрифт", "15 шрифт", "17 шрифт", "19 шрифт", "21 шрифт", "23 шрифт", "25 шрифт"],
	"currentCourse": "",
	"currentGroup": "",
	"currentFont": "15 шрифт",
	"lastSchedule": "",
	"schedule": "",
	"groupJson": "",
	"font": "14"
}


class JsonHandler:

	def __init__(self):
		self.default = default
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
					file.write(dumps(data, ensure_ascii=False, indent=4))

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
				file.write(dumps(data, ensure_ascii=False, indent=4))


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