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

import wx
from gui.statsView import StatsView
from gui import builtinStatsViews
from gui.utils.numberFormatter import formatAmount
import locale

try:
    from collections import OrderedDict
except ImportError:
    from utils.compat import OrderedDict

class TargetingMiscViewFull(StatsView):
    name = "targetingmiscViewFull"
    def __init__(self, parent):
        StatsView.__init__(self)
        self.parent = parent
        self._cachedValues = []
    def getHeaderText(self, fit):
        return u"锁定系统及其他"

    def getTextExtentW(self, text):
        width, height = self.parent.GetTextExtent( text )
        return width

    def populatePanel(self, contentPanel, headerPanel):
        contentSizer = contentPanel.GetSizer()

        self.panel = contentPanel
        self.headerPanel = headerPanel
        gridTargetingMisc = wx.FlexGridSizer(1, 3)
        contentSizer.Add( gridTargetingMisc, 0, wx.EXPAND | wx.ALL, 0)
        gridTargetingMisc.AddGrowableCol(0)
        gridTargetingMisc.AddGrowableCol(2)
        # Targeting

        gridTargeting = wx.FlexGridSizer(4, 2)
        gridTargeting.AddGrowableCol(1)

        gridTargetingMisc.Add(gridTargeting, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        labels = ((u"锁定目标数", "Targets", ""),
                  (u"锁定距离", "Range", "km"),
                  (u"扫描分辨率", "ScanRes", "mm"),
                  (u"感应强度", "SensorStr", ""),
                  (u"无人机控制距离", "CtrlRange", "km"))

        for header, labelShort, unit in labels:
            gridTargeting.Add(wx.StaticText(contentPanel, wx.ID_ANY, "%s: " % header), 0, wx.ALIGN_LEFT)

            box = wx.BoxSizer(wx.HORIZONTAL)
            gridTargeting.Add(box, 0, wx.ALIGN_LEFT)

            lbl = wx.StaticText(contentPanel, wx.ID_ANY, "0 %s" %unit)
            setattr(self, "label%s" % labelShort, lbl)
            box.Add(lbl, 0, wx.ALIGN_LEFT)

            self._cachedValues.append({"main": 0})

        # Misc
        gridTargetingMisc.Add( wx.StaticLine( contentPanel, wx.ID_ANY, style = wx.VERTICAL),0, wx.EXPAND, 3 )
        gridMisc = wx.FlexGridSizer(4, 2)
        gridMisc.AddGrowableCol(1)
        gridTargetingMisc.Add(gridMisc,0 , wx.ALIGN_LEFT | wx.ALL, 5)

        labels = ((u"速度", "Speed", "m/s"),
                  (u"转向时间", "AlignTime", "s"),
                  (u"信号半径", "SigRadius", "m"),
                  (u"跃迁速度", "WarpSpeed", "AU/s"),
                  (u"货柜舱", "Cargo", u"m\u00B3"))

        for header, labelShort, unit in labels:
            gridMisc.Add(wx.StaticText(contentPanel, wx.ID_ANY, "%s: " % header), 0, wx.ALIGN_LEFT)

            box = wx.BoxSizer(wx.HORIZONTAL)
            gridMisc.Add(box, 0, wx.ALIGN_LEFT)

            lbl = wx.StaticText(contentPanel, wx.ID_ANY, "0 %s" % unit)
            setattr(self, "labelFull%s" % labelShort, lbl)
            box.Add(lbl, 0, wx.ALIGN_LEFT)

            self._cachedValues.append({"main": 0})


    def refreshPanel(self, fit):
        #If we did anything interesting, we'd update our labels to reflect the new fit's stats here

        cargoNamesOrder = OrderedDict((
            ("fleetHangarCapacity", "Fleet hangar"),
            ("shipMaintenanceBayCapacity", "Maintenance bay"),
            ("specialAmmoHoldCapacity", "Ammo hold"),
            ("specialFuelBayCapacity", "Fuel bay"),
            ("specialShipHoldCapacity", "Ship hold"),
            ("specialSmallShipHoldCapacity", "Small ship hold"),
            ("specialMediumShipHoldCapacity", "Medium ship hold"),
            ("specialLargeShipHoldCapacity", "Large ship hold"),
            ("specialIndustrialShipHoldCapacity", "Industrial ship hold"),
            ("specialOreHoldCapacity", "Ore hold"),
            ("specialMineralHoldCapacity", "Mineral hold"),
            ("specialMaterialBayCapacity", "Material bay"),
            ("specialGasHoldCapacity", "Gas hold"),
            ("specialSalvageHoldCapacity", "Salvage hold"),
            ("specialCommandCenterHoldCapacity", "Command center hold"),
            ("specialPlanetaryCommoditiesHoldCapacity", "Planetary goods hold"),
            ("specialQuafeHoldCapacity", "Quafe hold")
        ))

        cargoValues = {
            "main": lambda: fit.ship.getModifiedItemAttr("capacity"),
            "fleetHangarCapacity": lambda: fit.ship.getModifiedItemAttr("fleetHangarCapacity"),
            "shipMaintenanceBayCapacity": lambda: fit.ship.getModifiedItemAttr("shipMaintenanceBayCapacity"),
            "specialAmmoHoldCapacity": lambda: fit.ship.getModifiedItemAttr("specialAmmoHoldCapacity"),
            "specialFuelBayCapacity": lambda: fit.ship.getModifiedItemAttr("specialFuelBayCapacity"),
            "specialShipHoldCapacity": lambda: fit.ship.getModifiedItemAttr("specialShipHoldCapacity"),
            "specialSmallShipHoldCapacity": lambda: fit.ship.getModifiedItemAttr("specialSmallShipHoldCapacity"),
            "specialMediumShipHoldCapacity": lambda: fit.ship.getModifiedItemAttr("specialMediumShipHoldCapacity"),
            "specialLargeShipHoldCapacity": lambda: fit.ship.getModifiedItemAttr("specialLargeShipHoldCapacity"),
            "specialIndustrialShipHoldCapacity": lambda: fit.ship.getModifiedItemAttr("specialIndustrialShipHoldCapacity"),
            "specialOreHoldCapacity": lambda: fit.ship.getModifiedItemAttr("specialOreHoldCapacity"),
            "specialMineralHoldCapacity": lambda: fit.ship.getModifiedItemAttr("specialMineralHoldCapacity"),
            "specialMaterialBayCapacity": lambda: fit.ship.getModifiedItemAttr("specialMaterialBayCapacity"),
            "specialGasHoldCapacity": lambda: fit.ship.getModifiedItemAttr("specialGasHoldCapacity"),
            "specialSalvageHoldCapacity": lambda: fit.ship.getModifiedItemAttr("specialSalvageHoldCapacity"),
            "specialCommandCenterHoldCapacity": lambda: fit.ship.getModifiedItemAttr("specialCommandCenterHoldCapacity"),
            "specialPlanetaryCommoditiesHoldCapacity": lambda: fit.ship.getModifiedItemAttr("specialPlanetaryCommoditiesHoldCapacity"),
            "specialQuafeHoldCapacity": lambda: fit.ship.getModifiedItemAttr("specialQuafeHoldCapacity")
        }

        stats = (("labelTargets", {"main": lambda: fit.maxTargets}, 3, 0, 0, ""),
                 ("labelRange", {"main": lambda: fit.maxTargetRange / 1000}, 3, 0, 0, "km"),
                 ("labelScanRes", {"main": lambda: fit.ship.getModifiedItemAttr("scanResolution")}, 3, 0, 0, "mm"),
                 ("labelSensorStr", {"main": lambda: fit.scanStrength}, 3, 0, 0, ""),
                 ("labelCtrlRange", {"main": lambda: fit.extraAttributes["droneControlRange"] / 1000}, 3, 0, 0, "km"),
                 ("labelFullSpeed", {"main": lambda: fit.ship.getModifiedItemAttr("maxVelocity")}, 3, 0, 0, "m/s"),
                 ("labelFullAlignTime", {"main": lambda: fit.alignTime}, 3, 0, 0, "s"),
                 ("labelFullSigRadius", {"main": lambda: fit.ship.getModifiedItemAttr("signatureRadius")}, 3, 0, 9, ""),
                 ("labelFullWarpSpeed", {"main": lambda: fit.warpSpeed}, 3, 0, 0, "AU/s"),
                 ("labelFullCargo", cargoValues, 3, 0, 9, u"m\u00B3"))

        counter = 0
        RADII = [(u"太空舱",25), (u"截击舰",33), (u"护卫舰",38),
                 (u"驱逐舰", 83), (u"巡洋舰", 130),
                 (u"战列巡洋舰", 265),  (u"战列舰",420),
                 (u"航空母舰", 3000)]
        for labelName, valueDict, prec, lowest, highest, unit in stats:
            label = getattr(self, labelName)
            newValues = {}
            for valueAlias, value in valueDict.items():
                value = value() if fit is not None else 0
                value = value if value is not None else 0
                newValues[valueAlias] = value
            if self._cachedValues[counter] != newValues:
                mainValue = newValues["main"]
                otherValues = dict((k, newValues[k]) for k in filter(lambda k: k != "main", newValues))
                if labelName == "labelFullCargo":
                    # Get sum of all cargoholds except for maintenance bay
                    additionalCargo = sum(otherValues.values())
                    if additionalCargo > 0:
                        label.SetLabel("%s+%s %s" %(formatAmount(mainValue, prec, lowest, highest),
                                                    formatAmount(additionalCargo, prec, lowest, highest),
                                                    unit))
                    else:
                        label.SetLabel("%s %s" %(formatAmount(mainValue, prec, lowest, highest), unit))
                else:
                    label.SetLabel("%s %s" %(formatAmount(mainValue, prec, lowest, highest), unit))
                # Tooltip stuff
                if fit:
                    if labelName == "labelScanRes":
                        lockTime = "%s\n" % u"锁定时间".center(30)
                        for size, radius in RADII:
                            left = "%.1fs" % fit.calculateLockTime(radius)
                            right = "%s [%d]" % (size, radius)
                            lockTime += "%5s\t%s\n" % (left,right)
                        label.SetToolTip(wx.ToolTip(lockTime))
                    elif labelName == "labelFullSigRadius":
                        label.SetToolTip(wx.ToolTip(u"Probe Size: %.3f" % (fit.probeSize or 0) ))
                    elif labelName == "labelFullWarpSpeed":
                        label.SetToolTip(wx.ToolTip(u"最大跃迁距离: %.1f AU" % fit.maxWarpDistance))
                    elif labelName == "labelSensorStr":
                        if fit.jamChance > 0:
                           label.SetToolTip(wx.ToolTip(u"类型: %s\nECM概率: %.1f%%" % (_(fit.scanType), fit.jamChance)))
                        else:
                           label.SetToolTip(wx.ToolTip(u"类型: %s" % (_(fit.scanType))))
                    elif labelName == "labelFullAlignTime":
                        alignTime = u"转向:\t%.3fs"%mainValue
                        mass = u"质量:\t%skg"%locale.format('%d', fit.ship.getModifiedItemAttr("mass"), 1)
                        agility = u"惯性:\t%.3fx"%fit.ship.getModifiedItemAttr("agility")
                        label.SetToolTip(wx.ToolTip("%s\n%s\n%s" % (alignTime, mass, agility)))
                    elif labelName == "labelFullCargo":
                        tipLines = []
                        tipLines.append(u"货柜舱: %.1fm\u00B3 / %sm\u00B3"% (fit.cargoBayUsed, newValues["main"]))
                        for attrName, tipAlias in cargoNamesOrder.items():
                            if newValues[attrName] > 0:
                                tipLines.append(u"%s: %sm\u00B3"% (tipAlias, newValues[attrName]))
                        label.SetToolTip(wx.ToolTip(u"\n".join(tipLines)))
                    else:
                        label.SetToolTip(wx.ToolTip("%.1f" % mainValue))
                else:
                    label.SetToolTip(wx.ToolTip(""))
                self._cachedValues[counter] = newValues
            elif labelName == "labelFullWarpSpeed":
                if fit:
                    label.SetToolTip(wx.ToolTip(u"最大跃迁距离: %.1f AU" % fit.maxWarpDistance))
                else:
                    label.SetToolTip(wx.ToolTip(""))
            elif labelName == "labelSensorStr":
                if fit:
                    if fit.jamChance > 0:
                        label.SetToolTip(wx.ToolTip(u"类型: %s\nECM概率: %.1f%%" % (_(fit.scanType), fit.jamChance)))
                    else:
                        label.SetToolTip(wx.ToolTip(u"类型: %s" % (_(fit.scanType))))
                else:
                    label.SetToolTip(wx.ToolTip(""))
            elif labelName == "labelFullCargo":
                if fit:
                    cachedCargo = self._cachedValues[counter]
                    # if you add stuff to cargo, the capacity doesn't change and thus it is still cached
                    # This assures us that we force refresh of cargo tooltip
                    tipLines = []
                    tipLines.append(u"货柜舱: %.1fm\u00B3 / %sm\u00B3"% (fit.cargoBayUsed, cachedCargo["main"]))
                    for attrName, tipAlias in cargoNamesOrder.items():
                        if cachedCargo[attrName] > 0:
                            tipLines.append(u"%s: %sm\u00B3"% (tipAlias, cachedCargo[attrName]))
                    label.SetToolTip(wx.ToolTip(u"\n".join(tipLines)))
                else:
                    label.SetToolTip(wx.ToolTip(""))

            counter += 1

        self.panel.Layout()
        self.headerPanel.Layout()

TargetingMiscViewFull.register()
