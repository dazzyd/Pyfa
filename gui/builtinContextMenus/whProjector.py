# -*- coding: utf-8 -*-
from gui.contextMenu import ContextMenu
import gui.mainFrame
import gui.globalEvents as GE
import service
import wx

class WhProjector(ContextMenu):
    def __init__(self):
        self.mainFrame = gui.mainFrame.MainFrame.getInstance()

    def display(self, srcContext, selection):
        return srcContext == "projected"

    def getText(self, itmContext, selection):
        return u"添加星系效果"

    def getSubMenu(self, context, selection, rootMenu, i, pitem):
        msw = True if "wxMSW" in wx.PlatformInfo else False
        sMkt = service.Market.getInstance()
        effdata = sMkt.getSystemWideEffects()

        self.idmap = {}
        sub = wx.Menu()

        for swType in sorted(effdata):
            subItem = wx.MenuItem(sub, wx.ID_ANY, _(swType))
            grandSub = wx.Menu()
            subItem.SetSubMenu(grandSub)
            sub.AppendItem(subItem)

            for swData in sorted(effdata[swType], key=lambda tpl: tpl[2]):
                wxid = wx.NewId()
                swObj, swName, swClass = swData
                self.idmap[wxid] = (swObj, swName)
                grandSubItem = wx.MenuItem(grandSub, wxid, _(swClass))
                if msw:
                    rootMenu.Bind(wx.EVT_MENU, self.handleSelection, grandSubItem)
                else:
                    grandSub.Bind(wx.EVT_MENU, self.handleSelection, grandSubItem)
                grandSub.AppendItem(grandSubItem)
        return sub

    def handleSelection(self, event):
        #Skip events ids that aren't mapped

        swObj, swName = self.idmap.get(event.Id, (False, False))
        if not swObj and not swName:
            event.Skip()
            return

        sFit = service.Fit.getInstance()
        fitID = self.mainFrame.getActiveFit()
        sFit.project(fitID, swObj)
        wx.PostEvent(self.mainFrame, GE.FitChanged(fitID=fitID))

WhProjector.register()
