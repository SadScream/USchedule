# -*- coding: utf-8 -*-

from kivy.uix.screenmanager import Screen
from threading import Thread
from time import sleep
from datetime import datetime, timedelta
from tools_.scheduleParser import Document
from tools_.JsonHandler import JsonHandler
from kivy.utils import get_color_from_hex

from kivymd.uix.snackbar import Snackbar


config = JsonHandler()


class Snack(Snackbar):

	def __init__(self, text, duration = 3, **kwargs):
		self.text = text
		self.duration = duration

		super().__init__(**kwargs)


class Container(Screen):

	def __init__(self, screen_manager, **kwargs):
		self.screen_manager = screen_manager

		# переменная для запоминания того, что была нажата кнопка "Следующая неделя"
		# необходимо, чтобы когда пользователь нажимал "Обновить расписание" выходило все также расписание за следующую неделю, а не текущую
		self._next_week = False

		# содержимое скроллера шрифтов
		fonts_tuple = config.read("fonts")

		self.fonts = [
			{
			"viewclass": "MDMenuItem",
			"text": fonts_tuple[i],
			"callback": self.callback_for_font_items
			} for i in range(len(fonts_tuple))
		]
		super().__init__(**kwargs)

	def callback_for_font_items(self, *args):
		self.ids.fontSpinner.text = args[0]

	def pressed(self, instance, on_start_ = False, next_week = False):
		'''
		реакция на нажатие кнопки обновления/получения расписания
		'''
		self.turn(0)
		self.ids.scrollArea.scroll_y = 1	
		self.ids.scrollArea.do_scroll = False

		if next_week:
			self._next_week = True

		if self._next_week:
			next_week = 7

		self.thread = Thread(target=self.generateTable, args=(instance, on_start_, next_week))
		self.thread.start()

	def generateTable(self, instance=None, on_start_=False, next_week=False):
		'''
		формирование таблицы расписания
		'''

		last_state_text = instance.text # перед тем, как изменить на "Ожидайте", запоминаем, какая надпись была до
		instance.text = "Ожидайте"

		if not next_week:
			date = datetime.now().strftime("%d-%m-%Y")
		else:
			# timedelta(days=next_week) т.к next_week - целое число по умолчанию равное 7(см. kivy-разметку кнопки id:nextWeekButton)
			_date = datetime.strptime(str(datetime.now() + timedelta(days=next_week)).split(" ")[0], "%Y-%m-%d")
			date = _date.strftime("%d-%m-%Y")

		group = self.screen_manager.screens[1].ids.groupSpinner.text

		table = Document(group, date).complete() # получаем расписание в формате словаря

		if not table:
			# instance.text = "Обновить"

			Snack("Ошибка соединения", 3).show()
			self.turn(1)
			self.ids.scrollArea.do_scroll = True
			instance.text = last_state_text
			
			return False

		if last_state_text == "Получить":
			config.write("currentGroup", self.screen_manager.screens[1].ids.groupSpinner.text)
			config.write("currentCourse", self.screen_manager.screens[1].ids.courseSpinner.text)
			config.write("currentInst", self.screen_manager.screens[1].ids.instSpinner.text)

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
		
		config.write("groupJson", table["DAT"])
		instance.text = "Обновить"
		self.ids.scrollArea.do_scroll = True
		self.turn(1)

	def fontChanged(self):
		'''
		изменение размера шрифта
		'''
		config.write("currentFont", self.ids.fontSpinner.text)
		self.ids.rst.font_size = int(self.ids.fontSpinner.text.replace(" шрифт", ""))

	def scheduleChanged(self):
		'''
		реакция на изменение текста лейбла расписания id:rst
		'''
		config.write("schedule", self.ids.rst.text)

	def turn(self, state):
		'''
		state = False - disabled
		state = True - enabled
		'''
		if not state:
			self.ids.gotoSettings.disabled = True
			self.ids.fontSpinner.disabled = True
			self.ids.reloadBtn.disabled = True
		else:
			self.ids.gotoSettings.disabled = False
			self.ids.fontSpinner.disabled = False
			self.ids.reloadBtn.disabled = False


class Settings(Screen):

	def __init__(self, DB, screen_manager, **args):
		self.DB = DB
		self.screen_manager = screen_manager
		self.courses = []
		self.groups = []
		# self.line = f"[size=13][s]\n{'  '*round(self.width/2)}\n[/s][/size]"

		# содержимое скроллера институтов
		insts_tuple = tuple(DB.keys())
		self.insts = [
			{
			"viewclass": "MDMenuItem",
			"text": insts_tuple[i],
			"callback": lambda text: self.callback_for_items("insts", text)
			} for i in range(len(insts_tuple))
		]

		super().__init__(**args)

	def updatorSwitcherActive(self, active):
		'''
		реакция на изменение состояния селектора id:updatorSwitcher
		'''

		config.write("updateOnStart", active)

	def callback_for_items(self, obj, text):
		'''
		когда происходит выбор элемента MDMenuItem скроллера NewMenu, текст NewButton, владеющего NewMenu меняется на text
		'''

		if obj == "insts":
			self.ids.instSpinner.text = text
		elif obj == "courses":
			self.ids.courseSpinner.text = text
		elif obj == "groups":
			self.ids.groupSpinner.text = text

	def gotoPressed(self, next_week = False, current_week = False):
		'''
		реакция на нажатие кнопок "Назад", "Следующая неделя", "Текущая неделя"
		next_week - True если была нажата кнопка "Следующая неделя"
		current_week - True если была нажата кнопка "Текущая неделя"
		'''

		if not next_week:
			if current_week == True:
				self.ids.currentWeek.disabled = True
				self.ids.nextWeekButton.disabled = False
				self.screen_manager.screens[0]._next_week = False
				return self.screen_manager.screens[0].pressed(self.screen_manager.screens[0].ids.reloadBtn)

			if self.screen_manager.screens[0].ids.reloadBtn.text == "Получить":
				self.ids.currentWeek.disabled = True
				self.ids.nextWeekButton.disabled = False
				self.screen_manager.screens[0]._next_week = False
				self.screen_manager.screens[0].pressed(self.screen_manager.screens[0].ids.reloadBtn)
		elif next_week:
			self.ids.nextWeekButton.disabled = True
			self.ids.currentWeek.disabled = False
			self.screen_manager.screens[0].pressed(self.screen_manager.screens[0].ids.reloadBtn, next_week=next_week)

	def instChanged(self):
		'''
		реакция на смену института
		'''
		currentInst = config.read("currentInst")

		# получаем выбранный институт и заполняем заполняем скроллер курсов этого института
		DB_courses = self.DB[self.ids.instSpinner.text]
		courses = []

		if currentInst == "":
			config.write("currentInst", self.ids.instSpinner.text)

		courses = [k for k, v in DB_courses.items()]

		self.courses = [
			{
			"viewclass": "MDMenuItem",
			"text": courses[i],
			"callback": lambda text: self.callback_for_items("courses", text)
			} for i in range(len(courses))
		]

		if self.ids.courseSpinner.text != courses[0]:
			self.ids.courseSpinner.text = courses[0]
		else:
			self.courseChanged()


	def courseChanged(self):
		'''
		реакция на смену курса
		'''
		currentCourse = config.read("currentCourse")

		if currentCourse == "":
			config.write("currentCourse", self.ids.courseSpinner.text)

		# заполнение скроллера групп
		DB_courses = self.DB[self.ids.instSpinner.text]
		currentGroup = config.read("currentGroup")

		groups = DB_courses[self.ids.courseSpinner.text]

		self.groups = [
			{
			"viewclass": "MDMenuItem",
			"text": groups[i],
			"callback": lambda text: self.callback_for_items("groups", text)
			} for i in range(len(groups))
		]

		if self.ids.groupSpinner.text != groups[0]:
			self.ids.groupSpinner.text = groups[0]
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
				self.screen_manager.screens[0].ids.reloadBtn.text = "Обновить"
			else:
				self.screen_manager.screens[0].ids.reloadBtn.text = "Получить"