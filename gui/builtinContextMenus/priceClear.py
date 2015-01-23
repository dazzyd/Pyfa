# -*- coding: utf-8 -*-
from gui.contextMenu import ContextMenu
import gui.mainFrame
import wx
import gui.globalEvents as GE
import service

class PriceClear(ContextMenu):
    def __init__(self):
        self.mainFrame = gui.mainFrame.MainFrame.getInstance()

    def display(self, srcContext, selection):
        return srcContext == "priceViewFull"

    def getText(self, itmContext, selection):
        return u"清空价格缓存"

    def activate(self, fullContext, selection, i):
        sMkt = service.Market.getInstance()
        sMkt.clearPriceCache()
        wx.PostEvent(self.mainFrame, GE.FitChanged(fitID=self.mainFrame.getActiveFit()))

PriceClear.register()
