# -*- coding: utf-8 -*-
import wx

from gui.preferenceView import PreferenceView
from gui import bitmapLoader

import gui.mainFrame
import service
import gui.globalEvents as GE


class PFGeneralPref ( PreferenceView):
    title = "General"

    def populatePanel( self, panel ):
        self.mainFrame = gui.mainFrame.MainFrame.getInstance()
        self.dirtySettings = False
        self.openFitsSettings = service.SettingsProvider.getInstance().getSettings("pyfaPrevOpenFits", {"enabled": False, "pyfaOpenFits": []})

        mainSizer = wx.BoxSizer( wx.VERTICAL )

        self.stTitle = wx.StaticText( panel, wx.ID_ANY, self.title, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.stTitle.Wrap( -1 )
        self.stTitle.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )

        mainSizer.Add( self.stTitle, 0, wx.ALL, 5 )

        self.m_staticline1 = wx.StaticLine( panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        mainSizer.Add( self.m_staticline1, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 5 )

        self.cbGlobalChar = wx.CheckBox( panel, wx.ID_ANY, u"使用全局角色", wx.DefaultPosition, wx.DefaultSize, 0 )
        mainSizer.Add( self.cbGlobalChar, 0, wx.ALL|wx.EXPAND, 5 )

        self.cbGlobalDmgPattern = wx.CheckBox( panel, wx.ID_ANY, u"使用全局伤害类型", wx.DefaultPosition, wx.DefaultSize, 0 )
        mainSizer.Add( self.cbGlobalDmgPattern, 0, wx.ALL|wx.EXPAND, 5 )

        self.cbGlobalForceReload = wx.CheckBox( panel, wx.ID_ANY, u"计入装填时间", wx.DefaultPosition, wx.DefaultSize, 0 )
        mainSizer.Add( self.cbGlobalForceReload, 0, wx.ALL|wx.EXPAND, 5 )

        self.cbCompactSkills = wx.CheckBox( panel, wx.ID_ANY, u"使用紧凑的技能需求列表", wx.DefaultPosition, wx.DefaultSize, 0 )
        mainSizer.Add( self.cbCompactSkills, 0, wx.ALL|wx.EXPAND, 5 )

        self.cbFitColorSlots = wx.CheckBox( panel, wx.ID_ANY, u"装配窗口按槽位上色", wx.DefaultPosition, wx.DefaultSize, 0 )
        mainSizer.Add( self.cbFitColorSlots, 0, wx.ALL|wx.EXPAND, 5 )

        self.cbReopenFits = wx.CheckBox( panel, wx.ID_ANY, u"启动时恢复关闭前窗口", wx.DefaultPosition, wx.DefaultSize, 0 )
        mainSizer.Add( self.cbReopenFits, 0, wx.ALL|wx.EXPAND, 5 )

        self.cbRackSlots = wx.CheckBox( panel, wx.ID_ANY, u"分隔槽位", wx.DefaultPosition, wx.DefaultSize, 0 )
        mainSizer.Add( self.cbRackSlots, 0, wx.ALL|wx.EXPAND, 5 )

        labelSizer = wx.BoxSizer( wx.VERTICAL )
        self.cbRackLabels = wx.CheckBox( panel, wx.ID_ANY, u"显示槽位标签", wx.DefaultPosition, wx.DefaultSize, 0 )
        labelSizer.Add( self.cbRackLabels, 0, wx.ALL|wx.EXPAND, 5 )
        mainSizer.Add( labelSizer, 0, wx.LEFT|wx.EXPAND, 30 )

        self.cbShowTooltip = wx.CheckBox( panel, wx.ID_ANY, u"Show tab tooltips", wx.DefaultPosition, wx.DefaultSize, 0 )
        mainSizer.Add( self.cbShowTooltip, 0, wx.ALL|wx.EXPAND, 5 )

        defCharSizer = wx.BoxSizer( wx.HORIZONTAL )

        self.sFit = service.Fit.getInstance()

        self.cbGlobalChar.SetValue(self.sFit.serviceFittingOptions["useGlobalCharacter"])
        self.cbGlobalDmgPattern.SetValue(self.sFit.serviceFittingOptions["useGlobalDamagePattern"])
        self.cbGlobalForceReload.SetValue(self.sFit.serviceFittingOptions["useGlobalForceReload"])
        self.cbFitColorSlots.SetValue(self.sFit.serviceFittingOptions["colorFitBySlot"] or False)
        self.cbRackSlots.SetValue(self.sFit.serviceFittingOptions["rackSlots"] or False)
        self.cbRackLabels.SetValue(self.sFit.serviceFittingOptions["rackLabels"] or False)
        self.cbCompactSkills.SetValue(self.sFit.serviceFittingOptions["compactSkills"] or False)
        self.cbReopenFits.SetValue(self.openFitsSettings["enabled"])
        self.cbShowTooltip.SetValue(self.sFit.serviceFittingOptions["showTooltip"] or False)

        self.cbGlobalChar.Bind(wx.EVT_CHECKBOX, self.OnCBGlobalCharStateChange)
        self.cbGlobalDmgPattern.Bind(wx.EVT_CHECKBOX, self.OnCBGlobalDmgPatternStateChange)
        self.cbGlobalForceReload.Bind(wx.EVT_CHECKBOX, self.OnCBGlobalForceReloadStateChange)
        self.cbFitColorSlots.Bind(wx.EVT_CHECKBOX, self.onCBGlobalColorBySlot)
        self.cbRackSlots.Bind(wx.EVT_CHECKBOX, self.onCBGlobalRackSlots)
        self.cbRackLabels.Bind(wx.EVT_CHECKBOX, self.onCBGlobalRackLabels)
        self.cbCompactSkills.Bind(wx.EVT_CHECKBOX, self.onCBCompactSkills)
        self.cbReopenFits.Bind(wx.EVT_CHECKBOX, self.onCBReopenFits)
        self.cbShowTooltip.Bind(wx.EVT_CHECKBOX, self.onCBShowTooltip)

        self.cbRackLabels.Enable(self.sFit.serviceFittingOptions["rackSlots"] or False)

        panel.SetSizer( mainSizer )
        panel.Layout()

    def onCBGlobalColorBySlot(self, event):
        self.sFit.serviceFittingOptions["colorFitBySlot"] = self.cbFitColorSlots.GetValue()
        fitID = self.mainFrame.getActiveFit()
        self.sFit.refreshFit(fitID)
        wx.PostEvent(self.mainFrame, GE.FitChanged(fitID=fitID))
        event.Skip()

    def onCBGlobalRackSlots(self, event):
        self.sFit.serviceFittingOptions["rackSlots"] = self.cbRackSlots.GetValue()
        self.cbRackLabels.Enable(self.cbRackSlots.GetValue())
        fitID = self.mainFrame.getActiveFit()
        self.sFit.refreshFit(fitID)
        wx.PostEvent(self.mainFrame, GE.FitChanged(fitID=fitID))
        event.Skip()

    def onCBGlobalRackLabels(self, event):
        self.sFit.serviceFittingOptions["rackLabels"] = self.cbRackLabels.GetValue()
        fitID = self.mainFrame.getActiveFit()
        self.sFit.refreshFit(fitID)
        wx.PostEvent(self.mainFrame, GE.FitChanged(fitID=fitID))
        event.Skip()

    def OnCBGlobalForceReloadStateChange(self, event):
        self.sFit.serviceFittingOptions["useGlobalForceReload"] = self.cbGlobalForceReload.GetValue()
        fitID = self.mainFrame.getActiveFit()
        self.sFit.refreshFit(fitID)
        wx.PostEvent(self.mainFrame, GE.FitChanged(fitID=fitID))
        event.Skip()

    def OnCBGlobalCharStateChange(self, event):
        self.sFit.serviceFittingOptions["useGlobalCharacter"] = self.cbGlobalChar.GetValue()
        event.Skip()

    def OnCBGlobalDmgPatternStateChange(self, event):
        self.sFit.serviceFittingOptions["useGlobalDamagePattern"] = self.cbGlobalDmgPattern.GetValue()
        event.Skip()

    def onCBCompactSkills(self, event):
        self.sFit.serviceFittingOptions["compactSkills"] = self.cbCompactSkills.GetValue()
        fitID = self.mainFrame.getActiveFit()
        self.sFit.refreshFit(fitID)
        wx.PostEvent(self.mainFrame, GE.FitChanged(fitID=fitID))
        event.Skip()

    def onCBReopenFits(self, event):
        self.openFitsSettings["enabled"] = self.cbReopenFits.GetValue()

    def onCBShowTooltip(self, event):
        self.sFit.serviceFittingOptions["showTooltip"] = self.cbShowTooltip.GetValue()

    def getImage(self):
        return bitmapLoader.getBitmap("prefs_settings", "icons")

PFGeneralPref.register()
