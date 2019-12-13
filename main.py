# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

from threading import Thread
from json import loads
from time import sleep

from JsonHandler import JsonHandler
from DocumentHandler import Document



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

	GridLayout:
		rows: 2

		GridLayout:
			cols: 3
			size_hint_y: 0.053

			Button:
				text: 'Дополнительно'
				font_size: 14
				id: gotoSettings
				on_press:
					root.manager.current = 'settings'
					root.manager.transition.direction = 'right'

			Spinner:
				id: fontSpinner
				font_size: 14
				sync_height: True
				size: (150, 44)
				on_text: root.fontChanged()

			Button:
				id: reloadBtn
				font_size: 14

		BoxLayout:
			ScrollView:
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
	groupSpinner: groupSpinner
	courseSpinner: courseSpinner

	BoxLayout:
		BackgroundLabel:
			color: 0, 0, 0, 1
			background_color: .9, .9, .95, 1

	BoxLayout:
		orientation: 'vertical'

		Button:
			size_hint_y: 0.056
			id: gotoContainer
			text: 'Назад'
			on_press:
				root.manager.current = 'container'
				root.manager.transition.direction = 'left'
		
		BoxLayout:
			size_hint_y: 0.056
			orientation: 'horizontal'

			Spinner:
				id: courseSpinner
				sync_height: True
				on_text: root.courseChanged()

			Spinner:
				id: groupSpinner
				sync_height: True
				on_text: root.groupChanged()

		BoxLayout:
			margin: [0, 0, 0, 100]
"""



Config.set("graphics", "width", "360")
Config.set("graphics", "height", "640")

Builder.load_string(KV)


config = JsonHandler()


class Container(Screen):

	def pressed(self, instance):
		if instance.text == "Получить":
			config.write("currentGroup", settings.groupSpinner.text)
			config.write("currentCourse", settings.courseSpinner.text)

		self.turn(0)
		instance.text = "Ожидайте"
		thread = Thread(target=self.generateTable, args=(instance,))
		thread.start()

	def generateTable(self, instance=None):
		document = Document()
		self.rst.text = ' '
		text = ''

		with open("table.json", "r", encoding='utf-8') as file:
			table = loads(file.read())

		line = f"[size=13][s]\n{' '*round(self.width/3)}\n[/s][/size]"

		for j, (k, v) in enumerate(table.items()):
			if j > 1:
				if v[-1] == "-":
					v = v[:-1]
				text += f"\n[b]{k}[/b]:{line}"

				for i, item in enumerate(v):
					if i < len(v)-1:
						text += f"{' '*6}{item}{line}"
					else:
						text += f"{' '*6}{item}"

				text += line
			elif j == 0:
				text += f"{k}: {v}\n"
			elif j == 1:
				text += f"{k}: {v}\n\n"

		self.rst.text = text
		config.write("groupJson", document.tbl["Расписание для"])
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

	def groupChanged(self):
		tableGroup = config.read("groupJson")

		if len(tableGroup):
			if self.groupSpinner.text in tableGroup:
				container.reloadBtn.text = "Обновить"
			else:
				container.reloadBtn.text = "Получить"

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
		settings.courseSpinner.value = "Курс"
		settings.groupSpinner.value = "Группа"
		container.fontSpinner.value = "Шрифт"
		container.rst.text = lastSchedule

		# заполнение селекторов
		container.fontSpinner.values = tuple(fonts)
		settings.courseSpinner.values = tuple(_ for key in GAC for _, v in key.items())

		if not len(currentCourse) and not len(currentGroup):
			settings.courseSpinner.text = [k for k, v in GAC[0].items()][0]
		else:
			settings.courseSpinner.text = currentCourse
			settings.groupSpinner.text = currentGroup

		return screen_manager

if __name__ == '__main__':
	ScheduleApp().run()