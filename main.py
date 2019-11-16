__version__ = "1.1"

from kivy.app import App
from kivy.config import Config
from kivy.uix.gridlayout import GridLayout

from threading import Thread
from json import loads
from time import sleep

from JsonHandler import JsonHandler
from DocumentHandler import Document


Config.set("graphics", "width", "360")
Config.set("graphics", "height", "640")

config = JsonHandler()


class Container(GridLayout):

	def pressed(self, instance):
		if instance.text == "Получить":
			config.write("currentGroup", self.groupSpinner.text)
			config.write("currentCourse", self.courseSpinner.text)

		self.turn(0)
		instance.text = "Ожидайте"
		thread = Thread(target=self.generateTable, args=(instance,))
		thread.start()

	def generateTable(self, instance=None):
		document = Document()
		self.rst.text = ''

		with open("table.json", "r", encoding='utf-8') as file:
			table = loads(file.read())

		for j, (k, v) in enumerate(table.items()):
			if j > 1:
				self.rst.text += f"\n\n====\n\n**{k}**:\n\n"

				for i, item in enumerate(v):
					self.rst.text += f"{item}\n\n"
			elif j == 0:
				self.rst.text += f"{k}: {v}\n\n"
			elif j == 1:
				continue

		config.write("groupJson", document.tbl["Расписание для"])
		instance.text = "Обновить"
		self.turn(1)

	def fontChanged(self):
		config.write("currentFont", self.fontSpinner.text)
		self.rst.base_font_size = self.fontSpinner.text.replace(" шрифт", "sp")

	def scheduleChanged(self):
		config.write("schedule", self.rst.text)

	def groupChanged(self):
		tableGroup = config.read("groupJson")

		if len(tableGroup):
			if self.groupSpinner.text in tableGroup:
				self.reloadBtn.text = "Обновить"
			else:
				self.reloadBtn.text = "Получить"

	def courseChanged(self):
		GAC = config.read("courses")
		currentGroup = config.read("currentGroup")
		currentCourse = config.read("currentCourse")

		if currentCourse == "":
			config.write("currentCourse", self.courseSpinner.text)

		for i, item in enumerate(GAC):
			if self.courseSpinner.text in item:
				self.groupSpinner.values = tuple(GAC[i][self.courseSpinner.text])
				self.groupSpinner.text = GAC[i][self.courseSpinner.text][0]
				
				if currentGroup == "":
					config.write("currentGroup", self.groupSpinner.text)

	def turn(self, state):
		if state in [False, 0]:
			self.courseSpinner.disabled = True
			self.groupSpinner.disabled = True
			self.fontSpinner.disabled = True
			self.reloadBtn.disabled = True
		else:
			self.courseSpinner.disabled = False
			self.groupSpinner.disabled = False
			self.fontSpinner.disabled = False
			self.reloadBtn.disabled = False


class ScheduleApp(App):

	def build(self):
		container = Container()

		# бинд кнопок
		container.reloadBtn.bind(on_release=container.pressed)

		# получение наборов значений для селекторов
		GAC = config.read("courses") # groups and courses
		fonts = config.read("fonts")

		# получение последних значений селекторов, шрифта и расписания
		currentCourse = config.read("currentCourse")
		currentGroup = config.read("currentGroup")
		currentFont = config.read("currentFont")
		lastSchedule = config.read("schedule") # последнее расписание. пусто, если еще не запускалось

		# текущий размер шрифта
		container.fontSpinner.text = currentFont

		# текст кнопок
		container.reloadBtn.text = "Получить" if container.rst.text == "" else "Обновить"
		
		# установка значений селекторов и панели расписания
		container.courseSpinner.value = "Курс"
		container.groupSpinner.value = "Группа"
		container.fontSpinner.value = "Шрифт"
		container.rst.text = lastSchedule

		# заполнение селекторов
		container.fontSpinner.values = tuple(fonts)
		container.courseSpinner.values = tuple(_ for key in GAC for _, v in key.items())

		if not len(currentCourse) and not len(currentGroup):
			container.courseSpinner.text = [k for k, v in GAC[0].items()][0]
		else:
			container.courseSpinner.text = currentCourse
			container.groupSpinner.text = currentGroup	

		return container


if __name__ == '__main__':
	ScheduleApp().run()