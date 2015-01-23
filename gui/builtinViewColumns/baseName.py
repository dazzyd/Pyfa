# -*- coding: utf-8 -*-
#===============================================================================
# Copyright (C) 2010 Diego Duclos
#
# This file is part of pyfa.
#
# pyfa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyfa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyfa.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

from gui import builtinViewColumns
from gui.viewColumn import ViewColumn
from gui import bitmapLoader
import wx
from eos.types import Drone, Cargo, Fit, Module, Slot, Rack
import service

class BaseName(ViewColumn):
    name = "Base Name"
    def __init__(self, fittingView, params):
        ViewColumn.__init__(self, fittingView)
        self.columnText = u"名称"
        self.shipImage = fittingView.imageList.GetImageIndex("ship_small", "icons")
        self.mask = wx.LIST_MASK_TEXT

    def getText(self, stuff):
        if isinstance(stuff, Drone):
            return "%dx %s" % (stuff.amount, _(stuff.item.name))
        elif isinstance(stuff, Cargo):
            return "%dx %s" % (stuff.amount, _(stuff.item.name))
        elif isinstance(stuff, Fit):
            return "%s (%s)" % (_(stuff.name), _(stuff.ship.item.name))
        elif isinstance(stuff, Rack):
            if service.Fit.getInstance().serviceFittingOptions["rackLabels"]:
                if stuff.slot == Slot.MODE:
                    return u'─ 战术模式 ─'
                else:
                    slotName = {"high": u"高", "med": u"中", "low": u"低", "rig": u"改装件", "subsystem": u"子系统"}
                    return u"%s槽" % slotName[Slot.getName(stuff.slot).lower()]
            else:
                return ""
        elif isinstance(stuff, Module):
            if stuff.isEmpty:
                slotName = {"high": u"高", "med": u"中", "low": u"低", "rig": u"改装件", "subsystem": u"子系统"}
                return u"%s槽" % slotName[Slot.getName(stuff.slot).lower()]
            else:
                return _(stuff.item.name)
        else:
            item = getattr(stuff, "item", stuff)
            return _(item.name)

BaseName.register()
