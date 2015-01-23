# -*- coding: utf-8 -*-
from gui.contextMenu import ContextMenu
import gui.mainFrame
import wx
from gui.shipBrowser import FitSelected

class OpenFit(ContextMenu):
    def __init__(self):
        self.mainFrame = gui.mainFrame.MainFrame.getInstance()

    def display(self, srcContext, selection):
        return srcContext == "projectedFit"

    def getText(self, itmContext, selection):
        return u"在新标签页中打开装配"

    def activate(self, fullContext, selection, i):
        fit = selection[0]
        wx.PostEvent(self.mainFrame, FitSelected(fitID=fit.ID, startup=2))

OpenFit.register()
