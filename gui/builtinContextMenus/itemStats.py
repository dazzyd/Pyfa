# -*- coding: utf-8 -*-
from gui.contextMenu import ContextMenu
from gui.itemStats import ItemStatsDialog
import gui.mainFrame
import service
import wx

class ItemStats(ContextMenu):
    def __init__(self):
        self.mainFrame = gui.mainFrame.MainFrame.getInstance()

    def display(self, srcContext, selection):
        return srcContext in ("marketItemGroup", "marketItemMisc",
                              "fittingModule", "fittingCharge",
                              "fittingShip", "baseShip",
                              "cargoItem", "droneItem",
                              "implantItem", "boosterItem",
                              "skillItem", "projectedModule",
                              "projectedDrone", "projectedCharge")

    def getText(self, itmContext, selection):
        return u"{0}信息".format(_(itmContext) if itmContext is not None else u"物品")

    def activate(self, fullContext, selection, i):
        srcContext = fullContext[0]
        if srcContext == "fittingShip":
            fitID = self.mainFrame.getActiveFit()
            sFit = service.Fit.getInstance()
            stuff = sFit.getFit(fitID).ship
        else:
            stuff = selection[0]

        if srcContext == "fittingModule" and stuff.isEmpty:
            return

        mstate = wx.GetMouseState()
        reuse = False

        if mstate.CmdDown():
            reuse = True

        if self.mainFrame.GetActiveStatsWindow() is None and reuse:
            ItemStatsDialog(stuff, fullContext)

        elif reuse:
            lastWnd = self.mainFrame.GetActiveStatsWindow()
            pos = lastWnd.GetPosition()
            maximized = lastWnd.IsMaximized()
            if not maximized:
                size = lastWnd.GetSize()
            else:
                size = wx.DefaultSize
                pos = wx.DefaultPosition
            ItemStatsDialog(stuff, fullContext, pos, size, maximized)
            lastWnd.closeEvent(None)

        else:
            ItemStatsDialog(stuff, fullContext)

ItemStats.register()
