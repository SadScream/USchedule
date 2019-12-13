# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

from datetime import datetime
from threading import Thread
from json import loads
from time import sleep

from JsonHandler import JsonHandler
from scheduleParser import Document



KV = """
<BackgroundColor@Widget>
	background_color: (1, 1, 1, 1)
	canvas.before:
		Color:
			rgba: root.background_color
		Rectangle:
			size: self.size
			pos: self.pos

<BackgroundLabel@Label+BackgroundColor>
	background_color: (0, 0, 0, 0)


<Container>:
	rst: rst
	gotoSettings: gotoSettings
	fontSpinner: fontSpinner
	reloadBtn: reloadBtn
	scrollArea: scrollArea

	GridLayout:
		rows: 2

		GridLayout:
			cols: 3
			size_hint_y: 0.057

			Button:
				text: 'Дополнительно'
				font_size: '14sp'
				id: gotoSettings
				on_press:
					root.manager.current = 'settings'
					root.manager.transition.direction = 'right'

			Spinner:
				id: fontSpinner
				font_size: '14sp'
				sync_height: True
				size: (150, 44)
				on_text: root.fontChanged()

			Button:
				id: reloadBtn
				font_size: '14sp'

		BoxLayout:
			ScrollView:
				id: scrollArea
				scroll_timeout: 250
				padding: [0, 1, 0, 0]

				BackgroundLabel:
					color: (0, 0, 0, 1)
					background_color: (.9, .9, .9, 1)
					text_size: root.width, None
					size_hint_y: None
					halign: 'left'
					valign: 'top'
					id: rst
					text: ""
					height: self.texture_size[1]
					markup: True
					on_text: root.scheduleChanged()

<Settings>:
	gotoContainer: gotoContainer
	instSpinner: instSpinner
	groupSpinner: groupSpinner
	courseSpinner: courseSpinner

	BoxLayout:
		BackgroundLabel:
			color: 0, 0, 0, 1
			background_color: .9, .9, .95, 1

	BoxLayout:
		orientation: 'vertical'

		Button:
			size_hint_y: 0.065
			id: gotoContainer
			text: 'Назад'
			on_press:
				root.manager.current = 'container'
				root.manager.transition.direction = 'left'

		Spinner:
			id: instSpinner
			size_hint_y: 0.065
			sync_height: True
			on_text: root.instChanged()

		Spinner:
			id: courseSpinner
			size_hint_y: 0.065
			sync_height: True
			on_text: root.courseChanged()

		Spinner:
			id: groupSpinner
			size_hint_y: 0.065
			sync_height: True
			on_text: root.groupChanged()

		BoxLayout:
			margin: [0, 0, 0, 100]
"""



Config.set("graphics", "width", "360")
Config.set("graphics", "height", "640")
Config.set('graphics', 'fullscreen', False)
Config.write()

Builder.load_string(KV)


config = JsonHandler()


class Container(Screen):

	def pressed(self, instance):
		if instance.text == "Получить":
			config.write("currentGroup", settings.groupSpinner.text)
			config.write("currentCourse", settings.courseSpinner.text)
			config.write("currentInst", settings.instSpinner.text)

		self.turn(0)
		instance.text = "Ожидайте"
		thread = Thread(target=self.generateTable, args=(instance,))
		thread.start()

	def generateTable(self, instance=None): 
		date = datetime.now().strftime("%d-%m-%Y")
		group = settings.groupSpinner.text
		table = Document(group, date).complete()

		self.rst.text = ' '
		text = ''

		line = f"[size=13][s]\n{' '*round(self.width/3)}\n[/s][/size]"

		for j, (k, v) in enumerate(table.items()):
			if j == 0:
				text += f"{v}\n\n"

			elif j > 0:
				text += f"\n[b]{k}[/b]:{line}"
				j = 0

				for key, value in v.items():
					if value == "":
						value = "-"

					text += f"{key}: {value}{line}"

		self.rst.text = text
		self.scrollArea.scroll_y = 1
		config.write("groupJson", table["DAT"])
		instance.text = "Обновить"
		self.turn(1)

	def fontChanged(self):
		config.write("currentFont", self.fontSpinner.text)
		self.rst.font_size = int(self.fontSpinner.text.replace(" шрифт", ""))

	def scheduleChanged(self):
		config.write("schedule", self.rst.text)

	def turn(self, state):
		if state in [False, 0]:
			self.gotoSettings.disabled = True
			self.fontSpinner.disabled = True
			self.reloadBtn.disabled = True
		else:
			self.gotoSettings.disabled = False
			self.fontSpinner.disabled = False
			self.reloadBtn.disabled = False


class Settings(Screen):


	def instChanged(self):
		GAC = config.read("database")[self.instSpinner.text]
		currentInst = config.read("currentInst")

		courses = []

		if currentInst == "":
			config.write("currentInst", self.instSpinner.text)

		for item in GAC:
			for k, v in item.items():
				courses.append(k)

		self.courseSpinner.values = tuple(courses)

		if self.courseSpinner.text != courses[0]:
			self.courseSpinner.text = courses[0]
		else:
			self.courseChanged()


	def courseChanged(self):
		GAC = config.read("database")[self.instSpinner.text]
		currentCourse = config.read("currentCourse")
		currentGroup = config.read("currentGroup")

		if currentCourse == "":
			config.write("currentCourse", self.courseSpinner.text)

		for item in GAC:
			for k, v in item.items():
				if self.courseSpinner.text == k:
					self.groupSpinner.values = tuple(v)

					if self.groupSpinner.text != v[0]:
						self.groupSpinner.text = v[0]
					else:
						self.groupChanged()
					
					if currentGroup == "":
						config.write("currentGroup", self.groupSpinner.text)

	def groupChanged(self):
		tableGroup = config.read("groupJson")

		if len(tableGroup):
			if self.groupSpinner.text in tableGroup:
				container.reloadBtn.text = "Обновить"
			else:
				container.reloadBtn.text = "Получить"


screen_manager = ScreenManager()
screen_manager.add_widget(Container(name="container"))
screen_manager.add_widget(Settings(name="settings"))
container = screen_manager.screens[0]
settings = screen_manager.screens[1]


class ScheduleApp(App):

	def build(self):
		# бинд кнопок
		container.reloadBtn.bind(on_release=container.pressed)

		# получение наборов значений для селекторов
		GAC = config.read("database")
		fonts = config.read("fonts")

		# получение последних значений селекторов, шрифта и расписания
		currentInst = config.read("currentInst")
		currentCourse = config.read("currentCourse")
		currentGroup = config.read("currentGroup")
		currentFont = config.read("currentFont")
		lastSchedule = config.read("schedule") # последнее расписание. пусто, если еще не запускалось

		# текущий размер шрифта
		container.fontSpinner.text = currentFont

		# текст кнопок
		container.reloadBtn.text = "Получить" if container.rst.text == "" else "Обновить"
		
		# установка значений селекторов и панели расписания
		settings.instSpinner.value = "Институт"
		settings.courseSpinner.value = "Курс"
		settings.groupSpinner.value = "Группа"
		container.fontSpinner.value = "Шрифт"
		container.rst.text = lastSchedule

		# заполнение селекторов
		container.fontSpinner.values = tuple(fonts)

		settings.instSpinner.values = tuple(GAC.keys())

		if not len(currentInst):
			settings.instSpinner.text = [_ for _ in GAC.keys()][0]
			#  settings.courseSpinner.text = [itm for itm in GAC[[_ for _ in GAC.keys()][0]][0].keys()][0]
		else:
			settings.instSpinner.text = currentInst
			settings.courseSpinner.text = currentCourse
			settings.groupSpinner.text = currentGroup

		return screen_manager

if __name__ == '__main__':
	ScheduleApp().run()