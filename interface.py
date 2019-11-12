# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.config import Config
from kivy.uix.gridlayout import GridLayout

from threading import Thread
from json import loads
from time import sleep

from modules.JsonHandler import JsonHandler
from modules.DocumentHandler import Document

Config.set("graphics", "width", "360") # ширина
Config.set("graphics", "height", "640") # высота

config = JsonHandler()

class Container(GridLayout):

	def pressed(self, instance):
		self.courseSpinner.disabled = True
		self.groupSpinner.disabled = True
		instance.disabled = True
		instance.text = "Wait"
		thread = Thread(target=self.generateTable, args=(instance,))
		thread.start()

	def generateTable(self, instance=None):
		Document()

		table = {}
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
				self.rst.text += f"{k}: {v.replace('_', ' ')}\n"

		self.courseSpinner.disabled = False
		self.groupSpinner.disabled = False
		instance.disabled = False
		instance.text = "Update"


	def groupChanged(self):
		config.write("currentGroup", self.groupSpinner.text)


	def courseChanged(self):
		config.write("currentSheet", self.courseSpinner.text)


class ScheduleApp(App):

	def build(self):
		container = Container()
		courses = config.read("courses")
		groups = config.read("groups")
		currentCourse = config.read("currentSheet")
		currentGroup = config.read("currentGroup")
		container.courseSpinner.values = tuple(courses)
		container.groupSpinner.values = tuple(groups)
		container.reloadBtn.bind(on_release=container.pressed)

		if not len(currentCourse) and not len(currentGroup):
			container.courseSpinner.text = courses[0]
			container.groupSpinner.text = groups[0]	
		else:
			container.courseSpinner.text = currentCourse
			container.groupSpinner.text = currentGroup			

		return container

if __name__ == '__main__':
	ScheduleApp().run()