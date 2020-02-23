# -*- coding: utf-8 -*-

from kivymd.app import MDApp
from kivy.config import Config
from kivy.lang import Builder
from kivy.animation import Animation
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivymd.uix.button import BaseRectangularButton, BaseFlatButton

from kivymd.uix.menu import MDDropdownMenu
import kivymd.material_resources as m_res
from kivy.core.window import Window
from kivy.metrics import dp

# from kivy.utils import get_color_from_hex
# from kivymd.color_definitions import colors

from datetime import datetime
from threading import Thread
from time import sleep

from JsonHandler import JsonHandler
from scheduleParser import Document


KV = """
#:import MDDropdownMenu kivymd.uix.menu.MDDropdownMenu
#:import MDFlatButton kivymd.uix.button.MDFlatButton

<NonPressButton>
	text_color: (1, 1, 1, 1)
	md_bg_color: (0, 0, 0, 1)
	size_hint_x: 1
	# _md_bg_color_down: (0, 0, 0, 1)
	# _radius: '10dp'


<Container>:
	name: 'container'

	canvas:
		Color:
			rgba: 0.7411764705882353, 0.7411764705882353, 0.7411764705882353, 1
		Rectangle:
			size: self.size
			pos: self.pos

	GridLayout:
		rows: 3

		GridLayout:
			cols: 3
			size_hint_y: 0.057
			padding: 2
			spacing: dp(1)

			NonPressButton:
				id: gotoSettings
				text: 'Дополнительно'
				on_release:
					root.manager.current = 'settings'
					root.manager.transition.direction = 'right'

			NonPressButton:
				id: fontSpinner
				on_text: root.fontChanged()
				on_press: app.openMenu(self, app.fonts)
				# MDDropdownMenu(items=app.fonts, width_mult=3, _center=False).open(self)

			NonPressButton:
				id: reloadBtn

		GridLayout:
			cols: 1
			rows: 1
			padding: [0, 5]

			ScrollView:
				id: scrollArea
				scroll_timeout: 250
				padding: [0, 1, 0, 0]

				MDLabel:
					id: rst
					text_size: root.width, None
					size_hint_y: None
					background_color : 0, 0, 0, 0
					text: ""
					height: self.texture_size[1]
					markup: True
					on_text: root.scheduleChanged()

		AnchorLayout:
			id: errorLayout
			anchor_x: 'center'
			anchor_y: 'bottom'
			size_hint_y: 0

			canvas:
				Color:
					rgba: 0.3, 0.3, 0.3, 1
				Rectangle:
					size: self.size
					pos: self.pos

			Label:
				id: errorLabel
				text: ""
				color: (1, 0.2, 0.2, 1)

<Settings>:
	name: 'settings'

	canvas:
		Color:
			rgba: 0.7411764705882353, 0.7411764705882353, 0.7411764705882353, 1
		Rectangle:
			size: self.size
			pos: self.pos

	BoxLayout:
		orientation: 'vertical'
		padding: 2
		spacing: "2dp"

		NonPressButton:
			id: gotoContainer
			size_hint_y: 0.073
			text: 'Назад'

			on_release:
				root.gotoPressed()
				root.manager.current = 'container'
				root.manager.transition.direction = 'left'

		NonPressButton:
			id: instSpinner
			size_hint_y: 0.073
			on_text: root.instChanged()
			on_press: app.openMenu(self, app.insts)
			# MDDropdownMenu(items=app.insts, width_mult=3).open(self)

		NonPressButton:
			id: courseSpinner
			size_hint_y: 0.073
			on_text: root.courseChanged()
			on_press: app.openMenu(self, root.courses)
			# MDDropdownMenu(items=root.courses, width_mult=3).open(self)

		NonPressButton:
			id: groupSpinner
			size_hint_y: 0.073
			on_text: root.groupChanged()
			on_press: app.openMenu(self, root.groups)
			# MDDropdownMenu(items=root.groups, width_mult=3).open(self)

		GridLayout:
			padding: [0, 100]
"""


Config.set("graphics", "width", "360")
Config.set("graphics", "height", "640")
Config.set('graphics', 'fullscreen', False)
Config.write()

from kivymd.theming import ThemeManager

config = JsonHandler()


class NonPressButton(BaseRectangularButton, BaseFlatButton):
	# MDFlatButton но без BasePressedButton
	pass


class NewMenu(MDDropdownMenu):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def display_menu(self, caller):
		'''
		переопределение метода открытия меню у спиннеров
		'''

		c = caller.to_window(
			caller.center_x, caller.center_y
		)  # Starting coords

		target_width = self.width_mult * m_res.STANDARD_INCREMENT
		if target_width > Window.width:
			target_width = (
				int(Window.width / m_res.STANDARD_INCREMENT)
				* m_res.STANDARD_INCREMENT
			)

		target_height = sum([dp(48) for i in self.items])
		if 0 < self.max_height < target_height:
			target_height = self.max_height

		if self.ver_growth is not None:
			ver_growth = self.ver_growth
		else:
			if target_height <= c[1] - self.border_margin:
				ver_growth = "down"
			elif target_height < Window.height - c[1] - self.border_margin:
				ver_growth = "up"
			else:
				if c[1] >= Window.height - c[1]:
					ver_growth = "down"
					target_height = c[1] - self.border_margin
				else:
					ver_growth = "up"
					target_height = Window.height - c[1] - self.border_margin

		if self.hor_growth is not None:
			hor_growth = self.hor_growth
		else:
			if target_width <= Window.width - c[0] - self.border_margin:
				hor_growth = "right"
			elif target_width < c[0] - self.border_margin:
				hor_growth = "left"
			else:
				if Window.width - c[0] >= c[0]:
					hor_growth = "right"
					target_width = Window.width - c[0] - self.border_margin
				else:
					hor_growth = "left"
					target_width = c[0] - self.border_margin

		if ver_growth == "down":
			tar_y = c[1] - target_height
		else:
			tar_y = c[1]

		if hor_growth == "right":
			tar_x = c[0]
		else:
			tar_x = c[0] - target_width

		menu = self.ids.md_menu

		anim = Animation(
			x=tar_x,
			y=tar_y,
			width=target_width,
			height=target_height,
			duration=0,
			transition="out_quint",
		)
		menu.pos = c
		anim.start(menu)


class Container(Screen):

	def pressed(self, instance, start = False):
		self.turn(0)
		self.ids.scrollArea.scroll_y = 1	
		self.ids.scrollArea.do_scroll = False
		self.thread = Thread(target=self.generateTable, args=(instance, start))
		self.thread.start()

	def showError(self, text, layout, label):
		i = 0.0
		
		while True:
			if i > 0.03:
				label.text = text
				break

			i += 0.001
			sleep(0.01)
			layout.size_hint_y = i
		
		sleep(3)
		label.text = ""

		while True:
			if i <= 0:
				break

			i -= 0.001
			sleep(0.01)
			layout.size_hint_y = i
		
		self.ids.scrollArea.do_scroll = True
		return

	def generateTable(self, instance=None, start=False):
		state_text = instance.text
		instance.text = "Ожидайте"
		date = datetime.now().strftime("%d-%m-%Y")
		group = screen_manager.screens[1].ids.groupSpinner.text

		table = Document(group, date).complete()

		if not table:
			instance.text = "Обновить"

			self.turn(1)

			if not start:
				self.thread = Thread(target=self.showError, args=("Ошибка соединения", self.ids.errorLayout, self.ids.errorLabel))
				self.thread.start()
			else:
				self.scrollArea.do_scroll = True
			
			instance.text = state_text

			return False

		if state_text == "Получить":
			config.write("currentGroup", screen_manager.screens[1].ids.groupSpinner.text)
			config.write("currentCourse", screen_manager.screens[1].ids.courseSpinner.text)
			config.write("currentInst", screen_manager.screens[1].ids.instSpinner.text)

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

		if self.ids.rst.text != text:
			self.ids.rst.text = ' '
			self.ids.rst.text = text

		self.ids.scrollArea.do_scroll = True
		
		config.write("groupJson", table["DAT"])
		instance.text = "Обновить"
		self.turn(1)

	def fontChanged(self):
		config.write("currentFont", self.ids.fontSpinner.text)
		self.ids.rst.font_size = int(self.ids.fontSpinner.text.replace(" шрифт", ""))

	def scheduleChanged(self):
		config.write("schedule", self.ids.rst.text)

	def turn(self, state):
		if state in [False, 0]:
			self.ids.gotoSettings.disabled = True
			self.ids.fontSpinner.disabled = True
			self.ids.reloadBtn.disabled = True
		else:
			self.ids.gotoSettings.disabled = False
			self.ids.fontSpinner.disabled = False
			self.ids.reloadBtn.disabled = False


class Settings(Screen):

	def __init__(self, **args):
		self.courses = []
		self.groups = []
		super().__init__(**args)

	def callback_for_course_items(self, *args):
		self.ids.courseSpinner.text = args[0]

	def callback_for_group_items(self, *args):
		self.ids.groupSpinner.text = args[0]

	def gotoPressed(self):
		'''
		реакция на нажатие кнопки "Назад"
		'''

		if screen_manager.screens[0].ids.reloadBtn.text == "Получить":
			screen_manager.screens[0].pressed(screen_manager.screens[0].ids.reloadBtn)

	def instChanged(self):
		'''
		реакция на смену института
		'''
		currentInst = config.read("currentInst")

		if currentInst == "":
			config.write("currentInst", self.ids.instSpinner.text)

		# получаем выбранный институт и заполняем заполняем скроллер курсов этого института
		DB_courses = DB[self.ids.instSpinner.text]
		courses = []

		for item in DB_courses:
			for k, v in item.items():
				courses.append(k)

		self.courses = [{"viewclass": "MDMenuItem", "text": courses[i], "callback": self.callback_for_course_items} for i in range(len(courses))]
		# self.ids.courseSpinner.items = tuple(courses)

		if self.ids.courseSpinner.text != courses[0]:
			self.ids.courseSpinner.text = courses[0]
		else:
			self.courseChanged()


	def courseChanged(self):
		'''
		колбэк на смену курса
		'''

		currentCourse = config.read("currentCourse")

		if currentCourse == "":
			config.write("currentCourse", self.ids.courseSpinner.text)

		# заполнение скроллера групп
		DB_courses = DB[self.ids.instSpinner.text]
		currentGroup = config.read("currentGroup")

		for item in DB_courses:
			for k, v in item.items():
				if self.ids.courseSpinner.text == k:
					groups = tuple(v)
					self.groups = [{"viewclass": "MDMenuItem", "text": groups[i], "callback": self.callback_for_group_items} for i in range(len(groups))]

					if self.ids.groupSpinner.text != v[0]:
						self.ids.groupSpinner.text = v[0]
					else:
						self.groupChanged()
					
					if currentGroup == "":
						config.write("currentGroup", self.ids.groupSpinner.text)

	def groupChanged(self):
		'''
		реакция на смену группы
		'''

		tableGroup = config.read("groupJson")

		if len(tableGroup):
			if self.ids.groupSpinner.text in tableGroup:
				screen_manager.screens[0].ids.reloadBtn.text = "Обновить"
			else:
				screen_manager.screens[0].ids.reloadBtn.text = "Получить"


class ScheduleApp(MDApp):

	def __init__(self, **kwargs):
		# self.theme_cls.theme_style = "Light"

		self.theme_cls.primary_palette = "Gray"

		'''
		'Red' 'Pink' 'Purple' 'DeepPurple' 'Indigo' 'Blue' 
		'LightBlue' 'Cyan' 'Teal' 'Green' 'LightGreen' 'Lime' 
		'Yellow' 'Amber' 'Orange' 'DeepOrange' 'Brown' 'Gray' 'BlueGray'
		'''

		super().__init__(**kwargs)

	def openMenu(self, target_widget, items):
		# костыль для открытия оптимизорованной дропдаун менюшки

		widget = NewMenu(items=items, width_mult=3)
		widget.open(target_widget)

	def callback_for_font_items(self, *args):
		screen_manager.screens[0].ids.fontSpinner.text = args[0]

	def callback_for_inst_items(self, *args):
		screen_manager.screens[1].ids.instSpinner.text = args[0]

	def build(self):
		fonts = config.read("fonts")
		insts = tuple(DB.keys())

		self.fonts = [{"viewclass": "MDMenuItem","text": fonts[i], "callback": self.callback_for_font_items} for i in range(len(fonts))]
		self.insts = [{"viewclass": "MDMenuItem", "text": insts[i], "callback": self.callback_for_inst_items} for i in range(len(insts))]

		Builder.load_string(KV)
		screen_manager.add_widget(Container(name='container'))
		screen_manager.add_widget(Settings(name='settings'))
		container = screen_manager.screens[0]
		settings = screen_manager.screens[1]

		# бинд кнопок
		container.ids.reloadBtn.bind(on_release=container.pressed) # вроде это было сделано потому что по-другому не прикручивалось

		# получение последних значений селекторов, шрифта и расписания
		currentInst = config.read("currentInst")
		currentCourse = config.read("currentCourse")
		currentGroup = config.read("currentGroup")
		currentFont = config.read("currentFont")
		lastSchedule = config.read("schedule") # последнее расписание. пусто, если еще не запускалось

		# текущий размер шрифта
		if currentFont == "font":
			self.callback_for_font_items("15 шрифт")
		else:	
			container.ids.fontSpinner.text = currentFont

		# текст кнопок
		container.ids.rst.text = lastSchedule
		container.ids.reloadBtn.text = "Получить" if container.ids.rst.text == "" else "Обновить"

		if not len(currentInst):
			settings.ids.instSpinner.text = [_ for _ in DB.keys()][0]
		else:
			settings.ids.instSpinner.text = currentInst
			settings.ids.courseSpinner.text = currentCourse
			settings.ids.groupSpinner.text = currentGroup

		if container.ids.reloadBtn.text == "Обновить":
			container.pressed(container.ids.reloadBtn, start = True)

		return screen_manager

if __name__ == '__main__':
	DB = config.read("database")
	transition = NoTransition()
	# trans.duration = 0.1
	screen_manager = ScreenManager(transition=transition)
	ScheduleApp().run()