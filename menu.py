import pygame
from pygame.locals import *
from colors import *


class Menu(object):
	BACKGROUND_COLOR = (51, 51, 51)
	TEXT_COLOR = ICE
	SELECTION_COLOR = (96, 144, 145)

	def __init__(self, menu_entries, font, margins=(0, 0, 0, 0), pos=(0, 0)):
		self.menu_entries = menu_entries
		self.n_entries = len(menu_entries)
		self.font = font
		self.rendered_entries = []

		for entry in menu_entries:
			render = font.render(entry[0], True, self.TEXT_COLOR).convert_alpha()
			self.rendered_entries.append(render)

		if len(margins) == 2:
			self.margins = (margins[0], margins[1], margins[0], margins[1])
		elif len(margins) == 4:
			self.margins = margins
		else:
			raise ValueError("Margins shold be a couple or a quadruple")
		self.size = (self.get_width(), self.get_height())
		self.rect = pygame.Rect(pos, self.size)
		self.w, self.h = self.size
		self.prev_index = self.index = None
		self.choice = None

	def __getitem__(self, key):
		return self.menu_entries[key]

	def get_width(self):
		max_width = 0
		for entry in self.rendered_entries:
			max_width = max(max_width, entry.get_width())
		return max_width + self.margins[1] + self.margins[3]

	def get_height(self):
		return (self.font.get_linesize() * self.n_entries +
				self.margins[0] + self.margins[2])

	def handle_keydown(self, event):
		if event.type != KEYDOWN:
			raise ValueError("Event type must be KEYDOWN")
		elif event.key == K_UP:
			self.move_index(-1)
		elif event.key == K_DOWN:
			self.move_index(1)
		elif event.key == K_RETURN and self.index is not None:
			if self.menu_entries[self.index][1] is not None:
				self.menu_entries[self.index][1]()
			self.choice = self.index
			return self.choice

	def set_index(self, index):
		self.prev_index = self.index
		self.index = index % self.n_entries

		if self.index != self.prev_index:
			for i, entry in enumerate(self.menu_entries):
				entry_text, entry_callback = entry
				if i == self.index:
					render = self.font.render(entry_text, True, self.TEXT_COLOR, self.SELECTION_COLOR).convert_alpha()
					self.rendered_entries[i] = render
				elif i == self.prev_index:
					render = self.font.render(entry_text, True, self.TEXT_COLOR, self.BACKGROUND_COLOR).convert_alpha()
					self.rendered_entries[i] = render

	def move_index(self, amount):
		if self.index is None:
			self.set_index(0)
		else:
			self.set_index(self.index + amount)

	def handle_click(self, event):
		if event.type != MOUSEBUTTONDOWN:
			raise ValueError("Event type must be MOUSEBUTTONDOWN")
		elif event.button == 1:
			for i, entry in enumerate(self.rendered_entries):
				pos = (self.margins[3] + self.rect.x, self.margins[0] + self.rect.y + (i * self.font.get_linesize()))
				rect = pygame.Rect(pos, entry.get_size())

				if rect.collidepoint(event.pos):
					self.choice = i
					if self.menu_entries[i][1] is not None:
						self.menu_entries[i][1]()

			return self.choice

	def handle_mouse_motion(self, event):
		if event.type != MOUSEMOTION:
			raise ValueError("Event type must be MOUSEMOTION")
		for i, entry in enumerate(self.rendered_entries):
			pos = (self.margins[3] + self.rect.x, self.margins[0] + self.rect.y + (i * self.font.get_linesize()))
			rect = pygame.Rect(pos, entry.get_size())

			if rect.collidepoint(event.pos):
				self.set_index(i)
	
	def handle_events(self, event):
		if event.type == MOUSEMOTION:
			return self.handle_mouse_motion(event)
		if event.type == MOUSEBUTTONDOWN:
			return self.handle_click(event)
		if event.type == KEYDOWN:
			return self.handle_keydown(event)

	def render(self, surface=None):
		if surface is None:
			surface = pygame.Surface(self.size)

		surface.fill(self.BACKGROUND_COLOR)

		for i, entry in enumerate(self.rendered_entries):
			surface.blit(entry, (self.margins[3], i * self.font.get_linesize() + self.margins[0]))

		return surface
