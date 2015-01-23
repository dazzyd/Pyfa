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

import gui.mainFrame
import wx.lib.newevent
import wx.gizmos
from gui import bitmapLoader
import service
import gui.display as d
from gui.contextMenu import ContextMenu
from wx.lib.buttons import GenBitmapButton
import gui.globalEvents as GE

class CharacterEditor(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__ (self, parent, id=wx.ID_ANY, title=u"pyfa: 角色编辑器", pos=wx.DefaultPosition,
                            size=wx.Size(641, 600), style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT|wx.TAB_TRAVERSAL)

        i = wx.IconFromBitmap(bitmapLoader.getBitmap("character_small", "icons"))
        self.SetIcon(i)

        self.disableWin=  wx.WindowDisabler(self)
        self.SetSizeHintsSz(wx.Size(640, 600), wx.DefaultSize)
        self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.navSizer = wx.BoxSizer(wx.HORIZONTAL)

        sChar = service.Character.getInstance()
        charList = sChar.getCharacterList()
        charList.sort(key=lambda t: t[1])

        self.btnSave = wx.Button(self, wx.ID_SAVE)
        self.btnSave.Hide()
        self.btnSave.Bind(wx.EVT_BUTTON, self.processRename)

        self.characterRename = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_PROCESS_ENTER)
        self.characterRename.Hide()
        self.characterRename.Bind(wx.EVT_TEXT_ENTER, self.processRename)

        self.skillTreeChoice = wx.Choice(self, wx.ID_ANY, style=0)

        for id, name, active in charList:
            i = self.skillTreeChoice.Append(name, id)
            if active:
                self.skillTreeChoice.SetSelection(i)

        self.navSizer.Add(self.skillTreeChoice, 1, wx.ALL | wx.EXPAND, 5)

        buttons = (("new", wx.ART_NEW),
                   ("rename", bitmapLoader.getBitmap("rename", "icons")),
                   ("copy", wx.ART_COPY),
                   ("delete", wx.ART_DELETE))
        buttonsName = {"new": u"创建", "rename": u"重命名", "copy": u"复制","delete": u"删除"}

        size = None
        for name, art in buttons:
            bitmap = wx.ArtProvider.GetBitmap(art, wx.ART_BUTTON) if name != "rename" else art
            btn = wx.BitmapButton(self, wx.ID_ANY, bitmap)
            if size is None:
                size = btn.GetSize()

            btn.SetMinSize(size)
            btn.SetMaxSize(size)

            btn.SetToolTipString(u"%s角色" % buttonsName[name])
            btn.Bind(wx.EVT_BUTTON, getattr(self, name))
            setattr(self, "btn%s" % name.capitalize(), btn)
            self.navSizer.Add(btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)


        mainSizer.Add(self.navSizer, 0, wx.ALL | wx.EXPAND, 5)

        self.viewsNBContainer = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)

        self.sview = SkillTreeView(self.viewsNBContainer)
        self.iview = ImplantsTreeView(self.viewsNBContainer)
        #=======================================================================
        # RC2
        self.iview.Show(False)
        #=======================================================================
        self.aview = APIView(self.viewsNBContainer)

        self.viewsNBContainer.AddPage(self.sview, u"技能")

        #=======================================================================
        # Disabled for RC2
        # self.viewsNBContainer.AddPage(self.iview, "Implants")
        #=======================================================================
        self.viewsNBContainer.AddPage(self.aview, "API")

        mainSizer.Add(self.viewsNBContainer, 1, wx.EXPAND | wx.ALL, 5)

        bSizerButtons = wx.BoxSizer(wx.HORIZONTAL)

        self.btnOK = wx.Button(self, wx.ID_OK)
        bSizerButtons.Add(self.btnOK, 0, wx.ALL, 5)
        self.btnOK.Bind(wx.EVT_BUTTON, self.editingFinished)

        mainSizer.Add(bSizerButtons, 0, wx.ALIGN_RIGHT, 5)


        self.SetSizer(mainSizer)
        self.Layout()

        self.Centre(wx.BOTH)

        charID = self.getActiveCharacter()
        if sChar.getCharName(charID) in ("All 0", "All 5"):
            self.restrict()

        self.registerEvents()

        self.mainFrame = gui.mainFrame.MainFrame.getInstance()

    def editingFinished(self, event):
        del self.disableWin
        wx.PostEvent(self.mainFrame, GE.CharListUpdated())
        self.Destroy()

    def registerEvents(self):
        self.Bind(wx.EVT_CLOSE, self.closeEvent)
        self.skillTreeChoice.Bind(wx.EVT_CHOICE, self.charChanged)

    def closeEvent(self, event):
        del self.disableWin
        wx.PostEvent(self.mainFrame, GE.CharListUpdated())
        self.Destroy()

    def restrict(self):
        self.btnRename.Enable(False)
        self.btnDelete.Enable(False)
        self.aview.inputID.Enable(False)
        self.aview.inputKey.Enable(False)
        self.aview.charChoice.Enable(False)
        self.aview.btnFetchCharList.Enable(False)
        self.aview.btnFetchSkills.Enable(False)
        self.aview.stStatus.SetLabel("")
        self.aview.Layout()

    def unrestrict(self):
        self.btnRename.Enable(True)
        self.btnDelete.Enable(True)
        self.aview.inputID.Enable(True)
        self.aview.inputKey.Enable(True)
        self.aview.btnFetchCharList.Enable(True)
        self.aview.btnFetchSkills.Enable(True)
        self.aview.stStatus.SetLabel("")
        self.aview.Layout()

    def charChanged(self, event):
        self.sview.skillTreeListCtrl.DeleteChildren(self.sview.root)
        self.sview.populateSkillTree()
        sChar = service.Character.getInstance()
        charID = self.getActiveCharacter()
        if sChar.getCharName(charID) in ("All 0", "All 5"):
            self.restrict()
        else:
            self.unrestrict()

        wx.PostEvent(self, GE.CharChanged())
        if event is not None:
            event.Skip()

    def getActiveCharacter(self):
        selection = self.skillTreeChoice.GetCurrentSelection()
        return self.skillTreeChoice.GetClientData(selection) if selection is not None else None

    def new(self, event):
        sChar = service.Character.getInstance()
        charID = sChar.new()
        id = self.skillTreeChoice.Append(sChar.getCharName(charID), charID)
        self.skillTreeChoice.SetSelection(id)
        self.unrestrict()
        self.btnSave.SetLabel(u"创建")
        self.rename(None)
        self.charChanged(None)

    def rename(self, event):
        if event is not None:
            self.btnSave.SetLabel(u"重命名")
        self.skillTreeChoice.Hide()
        self.characterRename.Show()
        self.navSizer.Replace(self.skillTreeChoice, self.characterRename)
        self.characterRename.SetFocus()
        for btn in (self.btnNew, self.btnCopy, self.btnRename, self.btnDelete):
            btn.Hide()
            self.navSizer.Remove(btn)

        self.btnSave.Show()
        self.navSizer.Add(self.btnSave, 0, wx.ALIGN_CENTER)
        self.navSizer.Layout()

        sChar = service.Character.getInstance()
        currName = sChar.getCharName(self.getActiveCharacter())
        self.characterRename.SetValue(currName)
        self.characterRename.SetSelection(0, len(currName))

    def processRename(self, event):
        sChar = service.Character.getInstance()
        newName = self.characterRename.GetLineText(0)

        if newName == "All 0" or newName == "All 5":
            newName = newName + " bases are belong to us"

        charID = self.getActiveCharacter()
        sChar.rename(charID, newName)

        self.skillTreeChoice.Show()
        self.characterRename.Hide()
        self.navSizer.Replace(self.characterRename, self.skillTreeChoice)
        for btn in (self.btnNew, self.btnCopy, self.btnRename, self.btnDelete):
            btn.Show()
            self.navSizer.Add(btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)

        self.navSizer.Remove(self.btnSave)
        self.btnSave.Hide()
        self.navSizer.Layout()
        selection = self.skillTreeChoice.GetCurrentSelection()
        self.skillTreeChoice.Delete(selection)
        self.skillTreeChoice.Insert(newName, selection, charID)
        self.skillTreeChoice.SetSelection(selection)

    def copy(self, event):
        sChar = service.Character.getInstance()
        charID = sChar.copy(self.getActiveCharacter())
        id = self.skillTreeChoice.Append(sChar.getCharName(charID), charID)
        self.skillTreeChoice.SetSelection(id)
        self.unrestrict()
        self.btnSave.SetLabel(u"复制")
        self.rename(None)
        wx.PostEvent(self, GE.CharChanged())

    def delete(self, event):
        sChar = service.Character.getInstance()
        sChar.delete(self.getActiveCharacter())
        sel = self.skillTreeChoice.GetSelection()
        self.skillTreeChoice.Delete(sel)
        self.skillTreeChoice.SetSelection(sel - 1)
        newSelection = self.getActiveCharacter()
        if sChar.getCharName(newSelection) in ("All 0", "All 5"):
            self.restrict()

        wx.PostEvent(self, GE.CharChanged())

    def Destroy(self):
        sFit = service.Fit.getInstance()
        fitID = self.mainFrame.getActiveFit()
        if fitID is not None:
            sFit.clearFit(fitID)
            wx.PostEvent(self.mainFrame, GE.FitChanged(fitID=fitID))

        wx.Frame.Destroy(self)

class SkillTreeView (wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(500, 300), style=wx.TAB_TRAVERSAL)

        pmainSizer = wx.BoxSizer(wx.VERTICAL)

        tree = self.skillTreeListCtrl = wx.gizmos.TreeListCtrl(self, wx.ID_ANY, style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT)
        pmainSizer.Add(tree, 1, wx.EXPAND | wx.ALL, 5)


        self.imageList = wx.ImageList(16, 16)
        tree.SetImageList(self.imageList)
        self.skillBookImageId = self.imageList.Add(bitmapLoader.getBitmap("skill_small", "icons"))

        tree.AddColumn(u"技能")
        tree.AddColumn(u"等级")
        tree.SetMainColumn(0)

        self.root = tree.AddRoot("Skills")
        tree.SetItemText(self.root, "Levels", 1)

        tree.SetColumnWidth(0, 500)

        self.populateSkillTree()

        tree.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.expandLookup)
        tree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.scheduleMenu)

        srcContext = "skillItem"
        itemContext = "Skill"
        context = (srcContext, itemContext)
        self.statsMenu = ContextMenu.getMenu(None, context)
        self.levelChangeMenu = ContextMenu.getMenu(None, context) or wx.Menu()
        self.levelChangeMenu.AppendSeparator()
        self.levelIds = {}

        idUnlearned = wx.NewId()
        self.levelIds[idUnlearned] = u"未吸收"
        self.levelChangeMenu.Append(idUnlearned, u"未吸收")

        for level in xrange(6):
            id = wx.NewId()
            self.levelIds[id] = level
            self.levelChangeMenu.Append(id, u"等级 %d" % level)

        self.levelChangeMenu.Bind(wx.EVT_MENU, self.changeLevel)
        self.SetSizer(pmainSizer)

        self.Layout()

    def populateSkillTree(self):
        sChar = service.Character.getInstance()
        groups = sChar.getSkillGroups()
        imageId = self.skillBookImageId
        root = self.root
        tree = self.skillTreeListCtrl

        for id, name in groups:
            childId = tree.AppendItem(root, _(name), imageId)
            tree.SetPyData(childId, id)
            tree.AppendItem(childId, "dummy")

        tree.SortChildren(root)

    def expandLookup(self, event):
        root = event.Item
        tree = self.skillTreeListCtrl
        child, cookie = tree.GetFirstChild(root)
        if tree.GetItemText(child) == "dummy":
            tree.Delete(child)

            #Get the real intrestin' stuff
            sChar = service.Character.getInstance()
            char = self.Parent.Parent.getActiveCharacter()
            for id, name in sChar.getSkills(tree.GetPyData(root)):
                iconId = self.skillBookImageId
                childId = tree.AppendItem(root, _(name), iconId, data=wx.TreeItemData(id))
                level = sChar.getSkillLevel(char, id)
                if level == "Not learned":
                    level = u"未吸收"
                tree.SetItemText(childId, u"等级 %d" % level if isinstance(level, int) else level, 1)

            tree.SortChildren(root)

    def scheduleMenu(self, event):
        event.Skip()
        wx.CallAfter(self.spawnMenu, event.Item)

    def spawnMenu(self, item):
        self.skillTreeListCtrl.SelectItem(item)
        if self.skillTreeListCtrl.GetChildrenCount(item) > 0:
            return

        sChar = service.Character.getInstance()
        charID = self.Parent.Parent.getActiveCharacter()
        sMkt = service.Market.getInstance()
        if sChar.getCharName(charID) not in ("All 0", "All 5"):
            self.levelChangeMenu.selection = sMkt.getItem(self.skillTreeListCtrl.GetPyData(item))
            self.PopupMenu(self.levelChangeMenu)
        else:
            self.statsMenu.selection = sMkt.getItem(self.skillTreeListCtrl.GetPyData(item))
            self.PopupMenu(self.statsMenu)

    def changeLevel(self, event):
        level = self.levelIds.get(event.Id)
        if level is not None:
            sChar = service.Character.getInstance()
            charID = self.Parent.Parent.getActiveCharacter()
            selection = self.skillTreeListCtrl.GetSelection()
            skillID = self.skillTreeListCtrl.GetPyData(selection)

            self.skillTreeListCtrl.SetItemText(selection, u"等级 %d" % level if isinstance(level, int) else level, 1)
            sChar.changeLevel(charID, skillID, level)

        event.Skip()


class ImplantsTreeView (wx.Panel):
    def addMarketViewImage(self, iconFile):
        if iconFile is None:
            return -1
        bitmap = bitmapLoader.getBitmap(iconFile, "pack")
        if bitmap is None:
            return -1
        else:
            return self.availableImplantsImageList.Add(bitmap)

    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(500, 300), style=wx.TAB_TRAVERSAL)

        pmainSizer = wx.BoxSizer(wx.HORIZONTAL)

        availableSizer = wx.BoxSizer(wx.VERTICAL)
        pmainSizer.Add(availableSizer, 1, wx.ALL | wx.EXPAND, 5)

        self.availableImplantsSearch = wx.SearchCtrl(self, wx.ID_ANY, style=wx.TE_PROCESS_ENTER)
        self.availableImplantsSearch.ShowCancelButton(True)
        availableSizer.Add(self.availableImplantsSearch, 0, wx.BOTTOM | wx.EXPAND, 2)

        self.availableImplantsTree = wx.TreeCtrl(self, wx.ID_ANY, style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT)
        root = self.availableRoot = self.availableImplantsTree.AddRoot("Available")
        self.availableImplantsImageList = wx.ImageList(16, 16)
        self.availableImplantsTree.SetImageList(self.availableImplantsImageList)

        availableSizer.Add(self.availableImplantsTree, 1, wx.EXPAND)

        buttonSizer = wx.BoxSizer(wx.VERTICAL)
        pmainSizer.Add(buttonSizer, 0, wx.TOP, 5)

        self.btnAdd = GenBitmapButton(self, wx.ID_ADD, bitmapLoader.getBitmap("fit_add_small", "icons"), style = wx.BORDER_NONE)
        buttonSizer.Add(self.btnAdd, 0)
        self.btnRemove = GenBitmapButton(self, wx.ID_REMOVE, bitmapLoader.getBitmap("fit_delete_small", "icons"), style = wx.BORDER_NONE)
        buttonSizer.Add(self.btnRemove, 0)

        self.pluggedImplantsTree = AvailableImplantsView(self, style=wx.LC_SINGLE_SEL)

        pmainSizer.Add(self.pluggedImplantsTree, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(pmainSizer)

        # Populate the market tree
        sMkt = service.Market.getInstance()
        for mktGrp in sMkt.getImplantTree():
            iconId = self.addMarketViewImage(sMkt.getIconByMarketGroup(mktGrp))
            childId = self.availableImplantsTree.AppendItem(root, mktGrp.name, iconId, data=wx.TreeItemData(mktGrp.ID))
            if sMkt.marketGroupHasTypesCheck(mktGrp) is False:
                self.availableImplantsTree.AppendItem(childId, "dummy")

        self.availableImplantsTree.SortChildren(self.availableRoot)

        #Bind the event to replace dummies by real data
        self.availableImplantsTree.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.expandLookup)

        #Bind add & remove buttons
        self.btnAdd.Bind(wx.EVT_BUTTON, self.addImplant)
        self.btnRemove.Bind(wx.EVT_BUTTON, self.removeImplant)

        #Bind the change of a character*
        self.Parent.Parent.Bind(GE.CHAR_CHANGED, self.charChanged)
        self.Enable(False)
        self.Layout()

    def update(self, implants):
        self.implants = implants[:]
        self.implants.sort(key=lambda i: int(i.getModifiedItemAttr("implantness")))
        self.pluggedImplantsTree.update(self.implants)

    def charChanged(self, event):
        sChar = service.Character.getInstance()
        charID = self.Parent.Parent.getActiveCharacter()
        name = sChar.getCharName(charID)
        if name == "All 0" or name == "All 5":
            self.Enable(False)
        else:
            self.Enable(True)

        self.update(sChar.getImplants(charID))
        event.Skip()

    def expandLookup(self, event):
        tree = self.availableImplantsTree
        root = event.Item
        child, cookie = tree.GetFirstChild(root)
        text = tree.GetItemText(child)
        if text == "dummy" or text == "itemdummy":
            sMkt = service.Market.getInstance()
            #A DUMMY! Keeeel!!! EBUL DUMMY MUST DIAF!
            tree.Delete(child)

        if text == "dummy":
            #Add 'real stoof!' instead
            for id, name, iconFile, more in sMkt.getChildren(tree.GetPyData(root)):
                iconId = self.addMarketViewImage(iconFile)
                childId = tree.AppendItem(root, name, iconId, data=wx.TreeItemData(id))
                if more:
                    tree.AppendItem(childId, "dummy")
                else:
                    tree.AppendItem(childId, "itemdummy")

        if text == "itemdummy":
            sMkt = service.Market.getInstance()
            data, usedMetas = sMkt.getVariations(tree.GetPyData(root))
            for item in data:
                id = item.ID
                name = item.name
                iconFile = item.icon.iconFile
                iconId = self.addMarketViewImage(iconFile)
                tree.AppendItem(root, name, iconId, data=wx.TreeItemData(id))

        tree.SortChildren(root)

    def addImplant(self, event):
        root = self.availableImplantsTree.GetSelection()

        if not root.IsOk():
            return

        nchilds = self.availableImplantsTree.GetChildrenCount(root)
        sChar = service.Character.getInstance()
        charID = self.Parent.Parent.getActiveCharacter()
        if nchilds == 0:
            itemID = self.availableImplantsTree.GetPyData(root)
            sChar.addImplant(charID, itemID)
            self.update(sChar.getImplants(charID))

    def removeImplant(self, event):
        pos = self.pluggedImplantsTree.GetFirstSelected()
        if pos != -1:
            sChar = service.Character.getInstance()
            charID = self.Parent.Parent.getActiveCharacter()
            sChar.removeImplant(charID, self.implants[pos].slot)
            self.update(sChar.getImplants(charID))

class AvailableImplantsView(d.Display):
    DEFAULT_COLS = ["Base Name",
                    "attr:implantness"]

    def __init__(self, parent, style):
        d.Display.__init__(self, parent, style=style)

class APIView (wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(500, 300), style=wx.TAB_TRAVERSAL)
        self.Parent.Parent.Bind(GE.CHAR_CHANGED, self.charChanged)

        self.apiUrlCreatePredefined = u"https://community.eveonline.com/support/api-key/CreatePredefined?accessMask=8"
        self.apiUrlKeyList = u"https://community.eveonline.com/support/api-key/"

        pmainSizer = wx.BoxSizer(wx.VERTICAL)

        fgSizerInput = wx.FlexGridSizer(3, 2, 0, 0)
        fgSizerInput.AddGrowableCol(1)
        fgSizerInput.SetFlexibleDirection(wx.BOTH)
        fgSizerInput.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticIDText = wx.StaticText(self, wx.ID_ANY, u"keyID:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticIDText.Wrap(-1)
        fgSizerInput.Add(self.m_staticIDText, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)

        self.inputID = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizerInput.Add(self.inputID, 1, wx.ALL | wx.EXPAND, 5)

        self.m_staticKeyText = wx.StaticText(self, wx.ID_ANY, u"vCode:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticKeyText.Wrap(-1)
        fgSizerInput.Add(self.m_staticKeyText, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)

        self.inputKey = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizerInput.Add(self.inputKey, 0, wx.ALL | wx.EXPAND, 5)

        self.m_staticCharText = wx.StaticText(self, wx.ID_ANY, u"Character:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticCharText.Wrap(-1)
        fgSizerInput.Add(self.m_staticCharText, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)

        self.charChoice = wx.Choice(self, wx.ID_ANY, style=0)
        self.charChoice.Append("No Selection", 0)
        fgSizerInput.Add(self.charChoice, 1, wx.ALL | wx.EXPAND, 5)

        self.charChoice.Enable(False)

        pmainSizer.Add(fgSizerInput, 0, wx.EXPAND, 5)

        btnSizer = wx.BoxSizer( wx.HORIZONTAL )
        btnSizer.AddStretchSpacer()

        self.btnFetchCharList = wx.Button(self, wx.ID_ANY, u"Get Characters")
        btnSizer.Add(self.btnFetchCharList, 0, wx.ALL, 2)
        self.btnFetchCharList.Bind(wx.EVT_BUTTON, self.fetchCharList)

        self.btnFetchSkills =  wx.Button(self, wx.ID_ANY, u"Fetch Skills")
        btnSizer.Add(self.btnFetchSkills,  0, wx.ALL, 2)
        self.btnFetchSkills.Bind(wx.EVT_BUTTON, self.fetchSkills)
        self.btnFetchSkills.Enable(False)

        btnSizer.AddStretchSpacer()
        pmainSizer.Add(btnSizer, 0, wx.EXPAND, 5)

        self.stStatus = wx.StaticText(self,  wx.ID_ANY, wx.EmptyString)
        pmainSizer.Add(self.stStatus, 0, wx.ALL, 5)

        pmainSizer.AddStretchSpacer()
        self.stAPITip = wx.StaticText( self, wx.ID_ANY, u"You can create a pre-defined key here (only CharacterSheet is required):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.stAPITip.Wrap( -1 )

        pmainSizer.Add( self.stAPITip, 0, wx.ALL, 2 )

        self.hlEveAPI = wx.HyperlinkCtrl( self, wx.ID_ANY, self.apiUrlCreatePredefined, self.apiUrlCreatePredefined, wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
        pmainSizer.Add( self.hlEveAPI, 0, wx.ALL, 2 )

        self.stAPITip2 = wx.StaticText( self, wx.ID_ANY, u"Or, you can choose an existing key from:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.stAPITip2.Wrap( -1 )
        pmainSizer.Add( self.stAPITip2, 0, wx.ALL, 2 )

        self.hlEveAPI2 = wx.HyperlinkCtrl( self, wx.ID_ANY, self.apiUrlKeyList, self.apiUrlKeyList, wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
        pmainSizer.Add( self.hlEveAPI2, 0, wx.ALL, 2 )

        self.SetSizer(pmainSizer)
        self.Layout()
        self.charChanged(None)

    def charChanged(self, event):
        sChar = service.Character.getInstance()
        ID, key, char, chars = sChar.getApiDetails(self.Parent.Parent.getActiveCharacter())
        self.inputID.SetValue(str(ID))
        self.inputKey.SetValue(key)

        self.charChoice.Clear()

        if chars:
            for charName in chars:
                i = self.charChoice.Append(charName)
            self.charChoice.SetStringSelection(char)
            self.charChoice.Enable(True)
            self.btnFetchSkills.Enable(True)
        else:
            self.charChoice.Append("No characters...", 0)
            self.charChoice.SetSelection(0)
            self.charChoice.Enable(False)
            self.btnFetchSkills.Enable(False)


        if event is not None:
            event.Skip()

    def fetchCharList(self, event):
        self.stStatus.SetLabel("")
        if self.inputID.GetLineText(0) == "" or self.inputKey.GetLineText(0) == "":
            self.stStatus.SetLabel("Invalid keyID or vCode!")
            return

        sChar = service.Character.getInstance()
        try:
            list = sChar.charList(self.Parent.Parent.getActiveCharacter(), self.inputID.GetLineText(0), self.inputKey.GetLineText(0))
        except service.network.AuthenticationError, e:
            self.stStatus.SetLabel("Authentication failure. Please check keyID and vCode combination.")
        except service.network.TimeoutError, e:
            self.stStatus.SetLabel("Request timed out. Please check network connectivity and/or proxy settings.")
        except Exception, e:
            self.stStatus.SetLabel("Error:\n%s"%e.message)
        else:
            self.charChoice.Clear()
            for charName in list:
                i = self.charChoice.Append(charName)

            self.btnFetchSkills.Enable(True)
            self.charChoice.Enable(True)

            self.Layout()

            self.charChoice.SetSelection(0)

    def fetchSkills(self, event):
        charName = self.charChoice.GetString(self.charChoice.GetSelection())
        if charName:
            try:
                sChar = service.Character.getInstance()
                sChar.apiFetch(self.Parent.Parent.getActiveCharacter(), charName)
                self.stStatus.SetLabel("Successfully fetched %s\'s skills from EVE API." % charName)
            except Exception, e:
                self.stStatus.SetLabel("Unable to retrieve %s\'s skills. Error message:\n%s" % (charName, e))
