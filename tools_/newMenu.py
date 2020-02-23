from kivymd.uix.menu import MDDropdownMenu
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.metrics import dp


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

		target_width = self.width_mult * dp(56) # kivymd.material_resources.STANDARD_INCREMENT
		if target_width > Window.width:
			target_width = (
				int(Window.width / dp(56))
				* dp(56)
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