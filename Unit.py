# -*- coding: utf-8 -*-
#
#  Unit.py, Ice Emblem's unit class.
#
#  Copyright 2015 Elia Argentieri <elia.argentieri@openmailbox.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.


import pygame
import os.path
import random


class Unit(object):
	"""
	This class is a unit with stats
	"""
	def __init__(self, name, hp_max, hp, lv, e, strength, skill, spd, luck, defence, res, move, con, aid, trv, affin, cond, wrank):
		self.name	=	str(name)   	# name of the character
		self.hp_max	=	int(hp_max) 	# maximum hp
		self.hp 	=	int(hp)     	# current hp
		self.lv 	=	int(lv)     	# level
		self.e  	=	int(e)      	# experience
		self.strength = int(strength)	# strength determines the damage inflicted to the enemy
		self.skill	=	int(skill)  	# skill chance of hitting the enemy
		self.spd	=	int(spd)    	# speed chance to avoid enemy's attack
		self.luck	=	int(luck)   	# luck influences many things
		self.defence=	int(defence)	# defence reduces phisical damages
		self.res	=	int(res)    	# resistence reduces magical damages
		self.move	=	int(move)   	# movement determines how far the unit can move in a turn
		self.con	=	int(con)    	# constitution, or phisical size. affects rescues.
		self.aid	=	int(aid)    	# max rescuing constitution. units with lower con can be rescued.
		self.trv	=	trv         	# traveler. the unit with whom this unit is traveling.
		self.affin	=	affin       	# elemental affinity. determines compatibility with other units.
		self.cond	=	cond        	# health conditions.
		self.wrank	=	wrank       	# weapons' levels.
		self.items	=	[]          	# list of items
		self.played	=	False       	# wether unit was used or not in a turn
		self.color = None
		path = os.path.abspath('sprites/' + self.name + '.png')
		try:
			self.image = pygame.image.load(path).convert_alpha()
		except pygame.error, e:
			print("Couldn't load " + path)
			print(e)
			self.image = None

	def __str__(self):
		return """
Unit: "%s"
	HP: %d/%d
	LV: %d	E: %d
	Str: %d	Skill: %d
	Spd: %d	Luck: %d
	Def: %d	Res: %d
	Move: %d	Con: %d
	Aid: %d	Trv: %s
	Affin: %s	Cond: %s
	WRank: %s
	Items: %s
	Played: %s
""" % (self.name,
			self.hp, self.hp_max, self.lv, self.e, self.strength,
			self.skill, self.spd, self.luck, self.defence,
			self.res, self.move, self.con, self.aid, self.trv,
			self.affin, self.cond, self.wrank, self.items, self.played)

	def render_info(self, font):
		"""
		Returns a Surface containing all informations about a unit.
		The specified font will be used to render the text and will
		determine the width and haight of the Surface
		"""

		font_linesize = font.get_linesize()

		# will "parse" this text and render each attribute individually
		info_text = self.__str__()

		info_list = []
		max_width = 0
		counter = 0

		# which attributes to show
		show = ['HP', 'LV', 'E', 'Str', 'Skill', 'Spd', 'Luck', 'Def']

		# split newlines and tabs except the "indentation" tabs
		for raw_line in iter(info_text.splitlines()):
			for line in iter(raw_line.strip().split('\t')):
				attr = line.split(':')
				if attr[0] in show:
					# it's in the list: render it
					info_list.append(font.render(line, 1, (255, 255, 255)))
					# max_width and counter to compute surface's size
					max_width = max(info_list[-1].get_size()[0], max_width)
					counter += 1

		dim = (int(max_width * 2 + 20), int(counter * font_linesize / 2))
		surface = pygame.Surface(dim).convert_alpha()
		surface.fill((0, 0, 0, 0))  # transparent surface

		for i, line in enumerate(info_list):
			# position each attribute in two colums
			pos = (i % 2 * (max_width + 20), i / 2 * font_linesize)
			surface.blit(line, pos)

		return surface

	def get_active_weapon(self):
		"""Returns the active weapon if it exists, None otherwise."""
		for item in self.items:
			if item.active:
				return item
		return None

	def give_weapon(self, weapon, active=True):
		"""Gives a weapon to the unit. The weapon becomes active by default."""
		weapon.active = active
		self.items.append(weapon)

	def inflict_damage(self, dmg):
		"""Inflicts damages to the unit."""
		self.hp -= dmg
		if self.hp <= 0:
			self.hp = 0
			print("%s died" % self.name)

	def get_weapon_range(self):
		active_weapon = self.get_active_weapon()
		return active_weapon.range if active_weapon is not None else 1

	def get_attack_distance(self):
		return self.get_weapon_range() + self.move


	def number_of_attacks(self, enemy, distance):
		"""
		Returns a tuple: how many times this unit can attack the enemy
		and how many times the enemy can attack this unit in a single battle
		"""
		self_attacks = enemy_attacks = 1

		if self.spd > enemy.spd:
			self_attacks += 1
		elif enemy.spd > self.spd:
			enemy_attacks += 1

		self_range = self.get_weapon_range()
		enemy_range = enemy.get_weapon_range()
		if self_range < distance:
			self_attacks = 0
		if enemy_range < distance:
			enemy_attacks = 0

		return (self_attacks, enemy_attacks)

	def life_percent(self):
		return int(float(self.hp) / float(self.hp_max) * 100.0)

	def attack(self, enemy):
		"""
		This unit attacks another.
		0 -> miss
		1 -> hit
		2 -> broken weapon
		"""

		active_weapon = self.get_active_weapon()

		if active_weapon is None or active_weapon.uses == 0:
			dmg = self.strength - enemy.defence
			if dmg < 0:
				dmg = 0
			hit = self.skill * 2 + self.luck / 2
			print("%s attacks %s" % (self.name, enemy.name))
			print("Dmg: %d  Hit: %d" % (dmg, hit))
			if random.randrange(0, 100) > hit:
				print("%s misses %s" % (self.name, enemy.name))
				ret = 0
			else:
				print("%s inflicts %s %d damages" % (self.name, enemy.name, dmg))
				enemy.inflict_damage(dmg)
				ret = 1
		else:
			dmg = (self.strength + active_weapon.might) - enemy.defence # TODO
			if dmg < 0:
				dmg = 0
			hit = (self.skill * 2) + active_weapon.hit + (self.luck / 2)
			print("%s attacks %s using %s" % (self.name, enemy.name, active_weapon.name))
			print("Dmg: %d  Hit: %d" % (dmg, hit))
			if random.randrange(0, 100) > hit:
				print("%s misses %s" % (self.name, enemy.name))
				ret = 0
			else:
				print("%s inflicts %s %d damages" % (self.name, enemy.name, dmg))
				enemy.inflict_damage(dmg)
				if active_weapon.use() == 0:
					ret = 2
				else:
					ret = 1
		return ret


class Player(object):
	"""This class represents the player status and which units belong to."""

	number_of_players = 0

	def __init__(self, name, color, my_turn=False, units=[]):
		self.number_of_players += 1
		self.name = name
		for unit in units:
			unit.color = color
		self.units = units
		self.color = color
		self.my_turn = my_turn

	def __del__(self):
		self.number_of_players -= 1

	def __str__(self):
		units = "["
		for unit in self.units:
			units += unit.name + ', '
		return '%s: %s]' % (self.name, units)

	def is_mine(self, unit):
		"""Tells wether a unit belongs to this player or not"""
		return unit in self.units

	def is_turn_over(self):
		for unit in self.units:
			if not unit.played:
				return False
		return True

	def end_turn(self):
		for unit in self.units:
			unit.played = False
		self.my_turn = False
		print("Player %s ends its turn" % self.name)

	def begin_turn(self):
		self.my_turn = True
		for unit in self.units:
			unit.played = False
		print("Player %s begins its turn" % self.name)

	def is_defeated(self):
		return True if len(self.units) == 0 else False

	def remove_unit(self, unit):
		unit.color = None
		self.units.remove(unit)