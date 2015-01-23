# -*- coding: utf-8 -*-
import wx
from gui.contextMenu import ContextMenu
import gui.mainFrame
import service
from gui.shipBrowser import Stage3Selected

class ShipJump(ContextMenu):
    def __init__(self):
        self.mainFrame = gui.mainFrame.MainFrame.getInstance()

    def display(self, srcContext, selection):
        return srcContext == "fittingShip"

    def getText(self, itmContext, selection):
        return u"在舰船浏览器中打开"

    def activate(self, fullContext, selection, i):
        fitID = self.mainFrame.getActiveFit()
        sFit = service.Fit.getInstance()
        stuff = sFit.getFit(fitID).ship
        groupID = stuff.item.group.ID

        self.mainFrame.notebookBrowsers.SetSelection(1)
        wx.PostEvent(self.mainFrame.shipBrowser,Stage3Selected(shipID=stuff.item.ID, back=groupID))

ShipJump.register()
