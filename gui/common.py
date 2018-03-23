# -*- coding: utf-8 -*-
#
#  menu.py, Ice Emblem's menu class.
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

import room
import display


class Rect(pygame.Rect):
    def __init__(self, **kwargs):
        if 'rect' in kwargs:
            super().__init__(kwargs['rect'])
        else:
            super().__init__(0, 0, 0, 0)
        self.settings = {k: v for k, v in kwargs.items() if not k.startswith('_') and k in dir(self)}
        self.apply()

    def apply(self):
        for attr in self.settings:
            setattr(self, attr, self.settings[attr])


class TupleOp(tuple):
    def __new__(cls, *args):
        return tuple.__new__(cls, *args)
    def __add__(self, other):
        return TupleOp(x + y for x, y in zip(self, other))
    def __sub__(self, other):
        return self.__add__(-i for i in other)
    def __neg__(self):
        return TupleOp(-x for x in self)
    def __mul__(self, other):
        return TupleOp(x * other for x in self)
    def __truediv__(self, other):
        return TupleOp(x / other for x in self)
    def __floordiv__(self, other):
        return TupleOp(x // other for x in self)


class GUI(room.Room):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kwargs = kwargs
        self.user_interacted = False
        self.rect = Rect(**kwargs)
        self._content_size = self.rect.size
        self.padding = kwargs.get('padding', (0, 0, 0, 0))

    @property
    def content_size(self):
        return self._content_size

    @content_size.setter
    def content_size(self, size):
        self._content_size = size
        self.update_size()
        if isinstance(self.parent, GUI):
            self.parent.compute_content_size()

    def compute_content_size(self):
        self.rect.apply()

    @property
    def padding(self):
        return self._padding

    @padding.setter
    def padding(self, padding):
        self._padding = padding
        if isinstance(padding, int):

            self._padding = (padding,) * 4
        elif len(padding) == 2:
            self._padding = padding * 2
        elif len(padding) == 4:
            self._padding = padding
        else:
            raise ValueError("padding shold be either an int or a couple or a quadruple")
        self.update_size()

    def update_size(self):
        self.rect.size = (self.padding[1] + self.padding[3] + self.content_size[0],
                        self.padding[0] + self.padding[2] + self.content_size[1])

    def loop(self, _events, dt):
        super().loop(_events, dt)
        return self.user_interacted

    def global_coord(self, coord):
        coord = TupleOp(coord)
        node = self.parent
        while node is not None:
            if isinstance(node, GUI):
                coord += TupleOp(node.rect.topleft)
            node = node.parent
        return coord

    def global_pos(self):
        return self.global_coord(self.rect.topleft)

    def global_rect(self):
        return pygame.Rect(self.global_pos(), self.rect.size)

    def get_pos(self):
        return self.rect.topleft

    def get_size(self):
        return self.rect.size

    def get_width(self):
        return self.rect.w

    def get_height(self):
        return self.rect.h


class Image(GUI):
    def __init__(self, image, **kwargs):
        self.image = image
        super().__init__(size=image.get_size(), **kwargs)

    def compute_content_size(self):
        self.content_size = self.image.get_size()
        self.rect.apply()

    def draw(self, surface=display.window):
        surface.blit(self.image, self.rect)

