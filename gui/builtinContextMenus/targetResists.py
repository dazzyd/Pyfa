# -*- coding: utf-8 -*-
from gui.contextMenu import ContextMenu
import gui.mainFrame
import service
import gui.globalEvents as GE
import wx
from gui import bitmapLoader

try:
    from collections import OrderedDict
except ImportError:
    from gui.utils.compat import OrderedDict

class TargetResists(ContextMenu):
    def __init__(self):
        self.mainFrame = gui.mainFrame.MainFrame.getInstance()

    def display(self, srcContext, selection):
        if self.mainFrame.getActiveFit() is None or srcContext != "firepowerViewFull":
            return False

        sTR = service.TargetResists.getInstance()
        self.patterns = sTR.getTargetResistsList()
        self.patterns.sort(key=lambda p: (p.name in ["None"], p.name))

        return len(self.patterns) > 0

    def getText(self, itmContext, selection):
        return u"目标抗性"

    def handleResistSwitch(self, event):
        pattern = self.patternIds.get(event.Id, False)
        if pattern is False:
            event.Skip()
            return

        sFit = service.Fit.getInstance()
        fitID = self.mainFrame.getActiveFit()
        sFit.setTargetResists(fitID, pattern)
        wx.PostEvent(self.mainFrame, GE.FitChanged(fitID=fitID))

    def addPattern(self, rootMenu, pattern):
        id = wx.NewId()
        name = getattr(pattern, "_name", pattern.name) if pattern is not None else u"无抗性"

        self.patternIds[id] = pattern
        item = wx.MenuItem(rootMenu, id, name)
        rootMenu.Bind(wx.EVT_MENU, self.handleResistSwitch, item)

        # set pattern attr to menu item
        item.pattern = pattern

        # determine active pattern
        sFit = service.Fit.getInstance()
        fitID = self.mainFrame.getActiveFit()
        f = sFit.getFit(fitID)
        tr = f.targetResists

        if tr == pattern:
            bitmap = bitmapLoader.getBitmap("state_active_small", "icons")
            item.SetBitmap(bitmap)
        return item

    def getSubMenu(self, context, selection, rootMenu, i, pitem):
        msw = True if "wxMSW" in wx.PlatformInfo else False
        self.patternIds = {}
        self.subMenus = OrderedDict()
        self.singles  = []

        sub = wx.Menu()
        for pattern in self.patterns:
            start, end = pattern.name.find('['), pattern.name.find(']')
            if start is not -1 and end is not -1:
                currBase = pattern.name[start+1:end]
                # set helper attr
                setattr(pattern, "_name", pattern.name[end+1:].strip())
                if currBase not in self.subMenus:
                    self.subMenus[currBase] = []
                self.subMenus[currBase].append(pattern)
            else:
                self.singles.append(pattern)

        sub.AppendItem(self.addPattern(rootMenu if msw else sub, None))  # Add reset
        sub.AppendSeparator()

        # Single items, no parent
        for pattern in self.singles:
            sub.AppendItem(self.addPattern(rootMenu if msw else sub, pattern))

        # Items that have a parent
        for menuName, patterns in self.subMenus.items():
            # Create parent item for root menu that is simply name of parent
            item = wx.MenuItem(rootMenu, wx.NewId(), menuName)

            # Create menu for child items
            grandSub = wx.Menu()
            #sub.Bind(wx.EVT_MENU, self.handleResistSwitch)

            # Apply child menu to parent item
            item.SetSubMenu(grandSub)

            # Append child items to child menu
            for pattern in patterns:
                grandSub.AppendItem(self.addPattern(rootMenu if msw else grandSub, pattern))
            sub.AppendItem(item)  #finally, append parent item to root menu

        return sub

TargetResists.register()
