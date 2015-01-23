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
import config
import bitmapLoader
import gui.mainFrame
import gui.graphFrame
import gui.globalEvents as GE

class MainMenuBar(wx.MenuBar):
    def __init__(self):
        self.characterEditorId = wx.NewId()
        self.damagePatternEditorId = wx.NewId()
        self.targetResistsEditorId = wx.NewId()
        self.graphFrameId = wx.NewId()
        self.backupFitsId = wx.NewId()
        self.exportSkillsNeededId = wx.NewId()
        self.importCharacterId = wx.NewId()
        self.exportHtmlId = wx.NewId()
        self.wikiId = wx.NewId()
        self.forumId = wx.NewId()

        self.mainFrame = gui.mainFrame.MainFrame.getInstance()

        wx.MenuBar.__init__(self)

        # File menu
        fileMenu = wx.Menu()
        self.Append(fileMenu, u"文件 (F)")

        fileMenu.Append(self.mainFrame.addPageId, u"新建标签 (N)\tCTRL+T", "Open a new fitting tab")
        fileMenu.Append(self.mainFrame.closePageId, u"关闭标签 (C)\tCTRL+W", "Close the current fit")
        fileMenu.AppendSeparator()

        fileMenu.Append(self.backupFitsId, u"备份所有装配 (B)", "Backup all fittings to a XML file")
        fileMenu.Append(wx.ID_OPEN, u"导入装配 (I)\tCTRL+O", "Import fittings into pyfa")
        fileMenu.Append(wx.ID_SAVEAS, u"导出装配 (E)\tCTRL+S", "Export fitting to another format")
        fileMenu.AppendSeparator()
        fileMenu.Append(self.exportHtmlId, u"导出 HTML", "Export fits to HTML file (set in Preferences)")
        fileMenu.Append(self.exportSkillsNeededId, u"导出所需技能 (S)", "Export skills needed for this fitting")
        fileMenu.Append(self.importCharacterId, u"导入角色文件 (H)", "Import characters into pyfa from file")
        fileMenu.AppendSeparator()
        fileMenu.Append(wx.ID_EXIT, u"退出")

        # Edit menu
        editMenu = wx.Menu()
        self.Append(editMenu, u"编辑 (E)")

        #editMenu.Append(wx.ID_UNDO)
        #editMenu.Append(wx.ID_REDO)

        copyText = u"导出到剪贴板 (T)" + ("\tCTRL+C" if 'wxMSW' in wx.PlatformInfo else "")
        pasteText = u"从剪贴板导入 (F)" + ("\tCTRL+V" if 'wxMSW' in wx.PlatformInfo else "")
        editMenu.Append(wx.ID_COPY, copyText, "Export a fit to the clipboard")
        editMenu.Append(wx.ID_PASTE, pasteText, "Import a fit from the clipboard")

        # Character menu
        windowMenu = wx.Menu()
        self.Append(windowMenu, u"窗口 (W)")

        charEditItem = wx.MenuItem(windowMenu, self.characterEditorId, u"角色编辑器 (C)\tCTRL+E")
        charEditItem.SetBitmap(bitmapLoader.getBitmap("character_small", "icons"))
        windowMenu.AppendItem(charEditItem)

        damagePatternEditItem = wx.MenuItem(windowMenu, self.damagePatternEditorId, u"伤害类型编辑器\tCTRL+D")
        damagePatternEditItem.SetBitmap(bitmapLoader.getBitmap("damagePattern_small", "icons"))
        windowMenu.AppendItem(damagePatternEditItem)

        targetResistsEditItem = wx.MenuItem(windowMenu, self.targetResistsEditorId, u"目标抗性编辑器\tCTRL+R")
        targetResistsEditItem.SetBitmap(bitmapLoader.getBitmap("explosive_big", "icons"))
        windowMenu.AppendItem(targetResistsEditItem)

        graphFrameItem = wx.MenuItem(windowMenu, self.graphFrameId, u"伤害图表\tCTRL+G")
        graphFrameItem.SetBitmap(bitmapLoader.getBitmap("graphs_small", "icons"))
        windowMenu.AppendItem(graphFrameItem)

        preferencesItem = wx.MenuItem(windowMenu, wx.ID_PREFERENCES, u"参数设置\tCTRL+P")
        preferencesItem.SetBitmap(bitmapLoader.getBitmap("preferences_small", "icons"))
        windowMenu.AppendItem(preferencesItem)

        # Help menu
        helpMenu = wx.Menu()
        self.Append(helpMenu, u"帮助 (H)")
        helpMenu.Append(self.wikiId, u"Wiki", "Go to wiki on GitHub")
        helpMenu.Append(self.forumId, u"论坛", "Go to EVE Online Forum thread")
        helpMenu.AppendSeparator()
        helpMenu.Append(wx.ID_ABOUT, u"关于")

        if config.debug:
            helpMenu.Append( self.mainFrame.widgetInspectMenuID, "Open Widgets Inspect tool", "Open Widgets Inspect tool")

        self.mainFrame.Bind(GE.FIT_CHANGED, self.fitChanged)

    def fitChanged(self, event):
        enable = event.fitID is not None
        self.Enable(wx.ID_SAVEAS, enable)
        self.Enable(wx.ID_COPY, enable)
        self.Enable(self.exportSkillsNeededId, enable)
        event.Skip()

