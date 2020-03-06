# -*- coding: utf-8 -*-

from kivymd.app import MDApp
from kivy.base import EventLoop
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, NoTransition

# from kivy.utils import get_color_from_hex
# from kivymd.color_definitions import colors

from tools_.JsonHandler import JsonHandler
from tools_.newMenu import NewMenu
from tools_.kivy_cfg.Config import *
from tools_.newButton import NewButton
from tools_.screens import Container, Settings
from kivymd.theming import ThemeManager

from time import sleep as sleep_
from threading import Thread

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
				on_release: app.openMenu(self, root.fonts)

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
			rgba: 0.7411764705882353, 0.7411764705882353, 0.7411764705882353, 1
		Rectangle:
			size: self.size
			pos: self.pos

	# BoxLayout:
	# 	orientation: 'vertical'
	# 	padding: 2
	# 	spacing: "2dp"

	GridLayout:
		rows: 7
		cols: 1
		# size_hint_y: 0.073
		padding: 2
		spacing: "2dp"

		NewButton:
			id: gotoContainer
			# size_hint_y: 0.073
			text: 'Назад'

			on_release:
				root.gotoPressed()
				root.manager.current = 'container'
				root.manager.transition.direction = 'left'

		NewButton:
			id: instSpinner
			# size_hint_y: 0.073
			on_text: root.instChanged()
			on_press: Animation().stop_all(self)
			on_release: app.openMenu(self, root.insts)

		NewButton:
			id: courseSpinner
			# size_hint_y: 0.073
			on_text: root.courseChanged()
			on_press: Animation().stop_all(self)
			on_release: app.openMenu(self, root.courses)

		NewButton:
			id: groupSpinner
			# size_hint_y: 0.073
			on_text: root.groupChanged()
			on_press: Animation().stop_all(self)
			on_release: app.openMenu(self, root.groups)

		GridLayout:
			rows: 1
			cols: 1
			# padding: [0, 3]
			size_hint_y: 0

			canvas:
				Color:
					rgba: 0.06, 0.06, 0.06, 1
				Rectangle:
					size: (self.width, 2)
					pos: (self.pos[0], self.pos[1]-3)

		BoxLayout:
			orientation: 'vertical'
			size_hint_y: 0

			GridLayout:
				rows: 2
				cols: 1
				spacing: "2dp"
				padding: [0, 5]

				NewButton:
					id: nextWeekButton
					# size_hint_y: 0.073
					text: "Следующая неделя"
					on_press: Animation().stop_all(self)
					on_release:
						root.gotoPressed(next_week=7)
						root.manager.current = 'container'
						root.manager.transition.direction = 'left'

				NewButton:
					id: currentWeek
					# size_hint_y: 0.073
					text: "Текущая неделя"
					on_press: Animation().stop_all(self)
					disabled: True
					on_release:
						root.gotoPressed(current_week = True)
						root.manager.current = 'container'
						root.manager.transition.direction = 'left'

	GridLayout:
		padding: [0, 100]
"""


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

	def build(self):
		Builder.load_string(KV)
		screen_manager.add_widget(Container(screen_manager=screen_manager))
		screen_manager.add_widget(Settings(DB=DB, screen_manager=screen_manager))

		container = screen_manager.screens[0]
		settings = screen_manager.screens[1]

		# получение последних значений селекторов, шрифта и расписания
		currentInst = config.read("currentInst")
		currentCourse = config.read("currentCourse")
		currentGroup = config.read("currentGroup")
		currentFont = config.read("currentFont")
		lastSchedule = config.read("schedule") # последнее расписание. пусто, если еще не запускалось

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

		if screen_manager.screens[0].ids.reloadBtn.text == "Обновить":
			screen_manager.current = "settings"
			screen_manager.screens[1].ids.currentWeek.dispatch('on_release')

		return screen_manager

if __name__ == '__main__':
	config = JsonHandler() # creating and init app config
	DB = config.read("database")
	transition = NoTransition()
	# trans.duration = 0.1
	screen_manager = ScreenManager(transition=transition)
	ScheduleApp().run()