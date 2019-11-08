from kivy.app import App
from kivy.uix.button import Button
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout

Config.set("graphics", "resizable", "0")
Config.set("graphics", "width", "640")
Config.set("graphics", "height", "480")


class MyApp(App):

	def build(self):

		f1 = FloatLayout(size = (300, 300))

		f1.add_widget(Button(text = "кнопка", 
			background_color = [1, 0, 0, 1], 
			background_normal = "", 
			size_hint = (.5, .25), 
			pos = (10, 10)))

		return f1

if __name__ == '__main__':
	MyApp().run()