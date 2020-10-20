# -*- coding: utf-8 -*-

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, NoTransition

# from kivy.utils import get_color_from_hex
# from kivymd.color_definitions import colors

from tools_.JsonHandler import JsonHandler
from kivymd.uix.menu import MDDropdownMenu
from tools_.kivy_cfg.Config import *
from tools_.newButton import NewButton
from tools_.screens import Container, Settings

from datetime import datetime

'''
TODO:
	Расписание сессии(возможно когда-нибудь лет так через 100)
	Контакты
	Обновление базы институтов
'''


KV = """
#:import MDDropdownMenu kivymd.uix.menu.MDDropdownMenu
#:import MDFlatButton kivymd.uix.button.MDFlatButton
#:import Animation kivy.animation.Animation


<NewButton>
	text_color: (1, 1, 1, 1)
	md_bg_color: (0, 0, 0, 1)
	size_hint_x: 1
	# _md_bg_color_down: (0, 0, 0, 1)
	# _radius: '10dp'


<LineLayout@GridLayout>
	# orientation: 'vertical'
	rows: 1
	cols: 1
	size_hint: (1, None)
	height: 2

	canvas:
		Color:
			rgba: 0.05, 0.05, 0.05, 1
		Rectangle:
			size: (self.width, 2)
			pos: (self.pos[0], self.pos[1])


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

			NewButton:
				id: gotoSettings
				text: 'Дополнительно'
				on_release:
					root.manager.current = 'settings'
					root.manager.transition.direction = 'right'

			NewButton:
				id: fontSpinner
				on_text: root.fontChanged()
				on_press: Animation().stop_all(self)
				on_release: app.openMenu(self)

			NewButton:
				id: reloadBtn
				# on_press: Animation().stop_all(self)
				on_release: root.pressed(self)

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
			rgba: 0.74, 0.74, 0.74, 1
		Rectangle:
			size: self.size
			pos: self.pos

	StackLayout:
		orientation: 'tb-lr'
		padding: 2
		spacing: "2dp"

		NewButton:
			id: gotoContainer
			text: 'Назад'

			on_release:
				root.gotoPressed()
				root.manager.current = 'container'
				root.manager.transition.direction = 'left'

		NewButton:
			id: instSpinner
			on_text: root.instChanged()
			on_press: Animation().stop_all(self)
			on_release: app.openMenu(self)

		NewButton:
			id: courseSpinner
			on_text: root.courseChanged()
			on_press: Animation().stop_all(self)
			on_release: app.openMenu(self)

		NewButton:
			id: groupSpinner
			on_text: root.groupChanged()
			on_press: Animation().stop_all(self)
			on_release: app.openMenu(self)


		LineLayout:


		NewButton:
			id: nextWeekButton
			text: "Следующая неделя"
			on_press: Animation().stop_all(self)
			on_release:
				root.gotoPressed(next_week=7)
				root.manager.current = 'container'
				root.manager.transition.direction = 'left'

		NewButton:
			id: currentWeek
			text: "Текущая неделя"
			on_press: Animation().stop_all(self)
			disabled: True
			on_release:
				root.gotoPressed(current_week = True)
				root.manager.current = 'container'
				root.manager.transition.direction = 'left'


		LineLayout:


		GridLayout:
			rows: 1
			columns: 2
			spacing: '0dp'
			size_hint_y: 0.08

			MDLabel:
				id: updatorSwitcherButton
				text_size: '15sp'
				text: "Обновлять при запуске"

			MDSwitch:
				id: updatorSwitcher
				size_hint_x: 0.15
				width: dp(16)
				on_active: root.updatorSwitcherActive(self.active)


		LineLayout:


		GridLayout:
			rows: 1
			columns: 2
			spacing: '0dp'
			size_hint_y: 0.08

			MDLabel:
				id: nextWeekOnHolyday
				text_size: '15sp'
				text: "В воскресенье показывать расписание на следующую неделю"

			MDSwitch:
				id: nextWeekSwitcher
				size_hint_x: 0.15
				width: dp(16)
				on_active: root.nextWeekSwitcherActive(self.active)


		LineLayout:
"""


class ScheduleApp(MDApp):

	def openMenu(self, target_widget):
		# костыль для открытия оптимизорованной дропдаун менюшки


		if target_widget == screen_manager.screens[1].ids.instSpinner:
			target = screen_manager.screens[1].inst_menu
		elif target_widget == screen_manager.screens[1].ids.courseSpinner:
			target = screen_manager.screens[1].course_menu
		elif target_widget == screen_manager.screens[1].ids.groupSpinner:
			target = screen_manager.screens[1].group_menu
		elif target_widget == screen_manager.screens[0].ids.fontSpinner:
			target = screen_manager.screens[0].font_menu
		
		target.open()
		target.target_width += target.target_width/2

	def build(self):
		self.theme_cls.primary_palette = "Gray"

		Builder.load_string(KV)

		screen_manager.add_widget(Container(self, screen_manager=screen_manager))
		screen_manager.add_widget(Settings(self, DB=DB, screen_manager=screen_manager))

		screen_manager.screens[0].create_menus()
		screen_manager.screens[1].create_menus()

		container = screen_manager.screens[0]
		settings = screen_manager.screens[1]

		# получение последних значений селекторов, шрифта и расписания
		currentInst = config.read("currentInst")
		currentCourse = config.read("currentCourse")
		currentGroup = config.read("currentGroup")
		currentFont = config.read("currentFont")
		updateOnStart = config.read("updateOnStart")
		nextWeekOnHolyday = config.read("nextWeekOnHolyday")
		lastSchedule = config.read("schedule") # последнее расписание. пусто, если еще не запускалось

		# значение селекторов id:updatorSwitcher и id:nextWeekSwitcher
		settings.ids.updatorSwitcher.active = updateOnStart
		settings.ids.nextWeekSwitcher.active = nextWeekOnHolyday

		# текущий размер шрифта
		if currentFont == "font":
			container.callback_for_font_items("15 шрифт")
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

		dt = datetime.now()
		# dt = datetime(2020, 10, 18, 0, 0, 0, 0)
		isHolyday = (dt.weekday() == 6)

		if not isHolyday:
			if updateOnStart and screen_manager.screens[0].ids.reloadBtn.text == "Обновить":
				screen_manager.current = "settings"
				screen_manager.screens[1].ids.currentWeek.dispatch('on_release')
		else:
			if screen_manager.screens[0].ids.reloadBtn.text == "Обновить":
				screen_manager.screens[1].gotoPressed(next_week=1)

		return screen_manager

if __name__ == '__main__':
	# Clock.max_iteration = 100
	config = JsonHandler() # creating and init app config
	DB = config.read("database")
	transition = NoTransition()
	# trans.duration = 0.1
	screen_manager = ScreenManager(transition=transition)
	ScheduleApp().run()
