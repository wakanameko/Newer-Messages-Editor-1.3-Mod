#!/usr/bin/python
# -*- coding: utf-8 -*-

# Newer Messages Editor - Edits NewerSMBW's messages.bin
# Version 1.3-mod
# Copyright (C) 2013-2014 RoadrunnerWMC, 2023 @wakanameko2

# This file is part of Newer Messages Editor.

# Newer Messages Editor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Newer Messages Editor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Newer Messages Editor.  If not, see <http://www.gnu.org/licenses/>.



# newer_messages_editor.py
# This is the main executable for Newer Messages Editor


################################################################
################################################################


version = '1.3-mod'

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os

#setup
s = os.getcwd() #get path
print(s)
STpath = (f"{s}/data.txt") # get setting data path
print(STpath)
SFile = open(STpath, 'r') # open setting file
lines = SFile.readlines() # read setting file lines
print (lines)
# SFileAF = [line.rstrip("\n") for line in lines] # delete this -> '\n'
# print(SFileAF)

#===========about Setting File(/data.txt)===========#
#  EN -> MSLANG = 'English'   L -> VMode = 'Light'  #
#  JP -> MSLANG = 'Japanese'  D -> VMode = 'Dark'   #
#      example: ENL -> English & Light Mode         #
#===================================================#

with open(f"{s}/data.txt", "r") as f:
    for line in f:
        if "EN" in line:
            MSLANG = 'English'
            print('Selected EN!')
            
        else:
            MSLANG = 'Japanese'
            print('Selected JP!')

with open(f"{s}/data.txt", "r") as f:
    for line in f:
        if "L" in line:
            VMode = 'Light'
            print('Selected Light!')
            
        else:
            VMode = 'Dark'
            print('Selected Dark!')

StyleSheet = '''
QWidget {
    background-color: #15202B;
    color: #FEFFFE;
} 
QListWidget {
    background-color: #15202b;
}
QGroupBox {
    background-color: #111111;
}
QDialogButtonBox {
    background-color: #111111;
}
QPlainTextEdit {
    background-color: #15202b;
}
QDialog {
    background-color: #111111;
}
QLabel {
    background-color: #111111;
}
'''

################################################################
################################################################
################################################################
#################### File data Classes #########################


class Message():
    """Class that represents a message (ID, title, text)"""
    def __init__(self, id=0, title='New Message', text=''):
        """Inits the Message"""
        self.id = id
        self.title = title
        self.text = text

    def toPyObject(self):
        """Py2 / Py3 compatibility"""
        return self


class MessagesBin():
    """Class that represents Newer's Messages.bin"""
    def __init__(self, data=None):
        """Inits the MessagesBin"""
        self.Messages = []

        try: self.InitFromData(data)
        except: self.Messages = [] # erase corrupt data

    def InitFromData(self, data):
        """Inits the MessagesBin from file data"""
        # data[0:4] is the number of messages
        NumberOfMessages = (data[0] << 24) | (data[1] << 16) | (data[2] << 8) | data[3]
        
        # Get each message
        messages = []
        for i in range(NumberOfMessages):
            id = (data[(12*i)+4] << 24) | (data[(12*i)+5] << 16) | (data[(12*i)+6] << 8) | data[(12*i)+7]
            tOffset = (data[(12*i)+8] << 24) | (data[(12*i)+9] << 16) | (data[(12*i)+10] << 8) | data[(12*i)+11]
            bOffset = (data[(12*i)+12] << 24) | (data[(12*i)+13] << 16) | (data[(12*i)+14] << 8) | data[(12*i)+15]
            id -= 0x100

            # Get the title
            title = ''
            j = tOffset
            while True: # keep going until 0x0000 is found
                try: char = (data[j] << 8) | data[j+1] # 2 bytes per char
                except: break

                char = chr(char)
                
                if char == chr(0x00): break
                
                title += char
                j += 2

            # Get the text
            text = ''
            j = bOffset
            while True: # keep going until 0x0000 is found
                try: char = (data[j] << 8) | data[j+1] # 2 bytes per char
                except: break
                char = chr(char)
                if char == chr(0x00): break
                
                text += char
                j += 2

            messages.append(Message(id, title, text))

        # Assign it to self.Messages
        self.Messages = messages

    def save(self):
        """Returns data that can be saved to a file"""
        data = []

        # Add the number of messages
        M = len(self.Messages)
        data.append((M >> 24) & 0xFF)
        data.append((M >> 16) & 0xFF)
        data.append((M >>  8) & 0xFF)
        data.append((M >>  0) & 0xFF)

        # Find the expected text offset
        tOffset = 4 + 12*len(self.Messages)

        # Add text and offsets
        textData = []
        i = int(tOffset)
        for msg in self.Messages:
            # Add the ID
            id = 0x0100 + msg.id
            data.append((id >> 24) & 0xFF)
            data.append((id >> 16) & 0xFF)
            data.append((id >>  8) & 0xFF)
            data.append((id >>  0) & 0xFF)

            # Add the title offset
            data.append((i >> 24) & 0xFF)
            data.append((i >> 16) & 0xFF)
            data.append((i >>  8) & 0xFF)
            data.append((i >>  0) & 0xFF)

            # Add the title
            for j in msg.title: # each character
                char = ord(j)
                textData.append((char >> 8) & 0xFF)
                textData.append((char >> 0) & 0xFF)
                i += 2

            # Add two empty bytes
            textData.append(0)
            textData.append(0)
            i += 2

            # Add the text offset
            data.append((i >> 24) & 0xFF)
            data.append((i >> 16) & 0xFF)
            data.append((i >>  8) & 0xFF)
            data.append((i >>  0) & 0xFF)

            # Add the text
            for j in msg.text: # each character
                char = ord(j)
                textData.append((char >> 8) & 0xFF)
                textData.append((char >> 0) & 0xFF)
                i += 2

            # Add two empty bytes
            textData.append(0)
            textData.append(0)
            i += 2

        # Add the text data to the end of data
        for i in textData: data.append(i)

        # Return it
        if sys.version[0] == '2':
            new = ''
            for i in data: new += chr(i) # not chr
            return new
        else: return bytes(data)


################################################################
################################################################
################################################################
######################### UI Classes ###########################


class MessageViewer(QtWidgets.QWidget):
    """Widget that allows you to view the data in Message.bin"""

    # Drag-and-Drop Picker
    class DNDPicker(QtWidgets.QListWidget):
        """A list widget which calls a function when an item's been moved"""
        def __init__(self, handler):
            QtWidgets.QListWidget.__init__(self)
            self.handler = handler
            self.setDragDropMode(QtWidgets.QListWidget.InternalMove)
        def dropEvent(self, event):
            QtWidgets.QListWidget.dropEvent(self, event)
            self.handler()

    # Init
    def __init__(self):
        """Initialises the widget"""
        QtWidgets.QWidget.__init__(self)
        self.file = None

        # Create the message picker widgets
        if MSLANG == 'English':
            PickerBox = QtWidgets.QGroupBox('Messages')
            self.picker = self.DNDPicker(self.HandleDragDrop)
            self.ABtn = QtWidgets.QPushButton('Add')
            self.RBtn = QtWidgets.QPushButton('Remove')
            self.ABtn.setToolTip('<b>Add:</b><br>Adds a message to the end of the file')
            self.RBtn.setToolTip('<b>Remove:</b><br>Removes the currently selected file')
        else:
            PickerBox = QtWidgets.QGroupBox('メッセージ')
            self.picker = self.DNDPicker(self.HandleDragDrop)
            self.ABtn = QtWidgets.QPushButton('追加')
            self.RBtn = QtWidgets.QPushButton('削除')
            self.ABtn.setToolTip('<b>追加:</b><br>メッセージを追加します。')
            self.RBtn.setToolTip('<b>削除:</b><br>選択したメッセージを削除します。')

        # Connect them to handlers
        self.picker.currentItemChanged.connect(self.HandleMsgSel)
        self.ABtn.clicked.connect(self.HandleA)
        self.RBtn.clicked.connect(self.HandleR)

        # Disable them for now
        self.picker.setEnabled(False)
        self.ABtn.setEnabled(False)
        self.RBtn.setEnabled(False)

        # Set up the QGroupBox layout
        L = QtWidgets.QGridLayout()
        L.addWidget(self.picker, 0, 0, 1, 2)
        L.addWidget(self.ABtn, 1, 0)
        L.addWidget(self.RBtn, 1, 1)
        PickerBox.setLayout(L)

        # Create the message editor
        if MSLANG == 'English':
            self.MsgBox = QtWidgets.QGroupBox('Message') # assigned to self.MsgBox because the title changes later
        else:
            self.MsgBox = QtWidgets.QGroupBox('メッセージ')
        self.edit = MessageEditor()
        self.edit.dataChanged.connect(self.HandleMsgDatChange)
        L = QtWidgets.QVBoxLayout()
        L.addWidget(self.edit)
        self.MsgBox.setLayout(L)
        
        # Make the main layout
        L = QtWidgets.QHBoxLayout()
        L.addWidget(PickerBox)
        L.addWidget(self.MsgBox)
        self.setLayout(L)


    def setFile(self, file):
        """Changes the file to view"""
        self.file = file
        self.picker.clear()
        self.edit.clear()
        self.MsgBox.setTitle('Message')

        # Enable widgets
        self.picker.setEnabled(True)
        self.ABtn.setEnabled(True)
        self.RBtn.setEnabled(True)

        # Add messages
        for msg in file.Messages:
            item = QtWidgets.QListWidgetItem() # self.UpdateNames will add the name
            item.setData(QtCore.Qt.UserRole, msg)
            self.picker.addItem(item)

        self.UpdateNames()
        self.UpdateRBtn()

    def saveFile(self):
        """Returns the file in saved form"""
        return self.file.save() # self.file does this for us
    

    def UpdateNames(self):
        """Updates item names in the msg picker"""
        for item in self.picker.findItems('', QtCore.Qt.MatchContains):
            msg = item.data(QtCore.Qt.UserRole)
            text = str(msg.id) + ': ' + str(msg.title)
            item.setText(text)
            text = '<b> Message ' + str(msg.id) + ':</b><br>' + str(msg.text)
            item.setToolTip(text)

        # Rename the group box
        currentItem = self.picker.currentItem()
        
        if currentItem == None: return
        msg = currentItem.data(QtCore.Qt.UserRole)

        hexcode = '(0x' + hex(msg.id)[2:].upper() + ')'
        text = 'Message ' + str(msg.id) + ' ' + hexcode
        self.MsgBox.setTitle(text)


    def UpdateRBtn(self):
        """Enables/disables the Remove Last button"""
        self.RBtn.setEnabled(len(self.file.Messages) > 0)

    def HandleMsgDatChange(self):
        """Handles changes to the current message data"""
        self.UpdateNames()

    def HandleMsgSel(self):
        """Handles the user picking a message"""
        self.edit.clear()

        # Get the current item (it's None if nothing's selected)
        currentItem = self.picker.currentItem()

        # Enable/disable the Remove button
        self.RBtn.setEnabled(currentItem != None)

        # Get the message
        if currentItem == None: return
        msg = currentItem.data(QtCore.Qt.UserRole)

        # Set up the message editor
        self.edit.setMessage(msg)

        # Rename the group box
        self.UpdateNames()

    def HandleDragDrop(self):
        """Handles dragging and dropping"""
        # First, update the file
        newMessages = []
        for item in self.picker.findItems('', QtCore.Qt.MatchContains):
            msg = item.data(QtCore.Qt.UserRole)
            newMessages.append(msg)
        self.file.Messages = newMessages

        # Then, update the names
        self.UpdateNames()

    def HandleA(self):
        """Handles the user clicking Add"""
        msg = Message()
        if len(self.file.Messages) > 0: msg.id = self.file.Messages[-1].id + 1
        else: msg.id = 0
        self.file.Messages.append(msg)

        item = QtWidgets.QListWidgetItem() # self.UpdateNames will add the name
        item.setData(QtCore.Qt.UserRole, msg)
        self.picker.addItem(item)

        self.UpdateNames()
    def HandleR(self):
        """Handles the user clicking Remove"""
        item = self.picker.currentItem()
        msg = item.data(QtCore.Qt.UserRole)

        # Remove it from file and the picker
        self.file.Messages.remove(msg)
        self.picker.takeItem(self.picker.row(item))

        # Clear the selection
        self.edit.clear()
        self.picker.clearSelection()
        self.RBtn.setEnabled(False)

        self.UpdateNames()



class MessageEditor(QtWidgets.QWidget):
    """Widget that allows you to edit the data in a message"""
    dataChanged = QtCore.pyqtSignal()
    def __init__(self):
        """Initialises the MessageEditor"""
        QtWidgets.QWidget.__init__(self)
        self.msg = None

        # Create widgets
        self.id = QtWidgets.QSpinBox()
        self.id.setMaximum(255)
        self.title = QtWidgets.QLineEdit()
        self.title.setMaxLength(255)
        self.text = QtWidgets.QPlainTextEdit()
        self.text.setLineWrapMode(self.text.NoWrap)

        # Add some tooltips
        if MSLANG == 'English':
            self.id.setToolTip('<b>ID:</b><br>This is the value the Message Box sprite uses to find messages. Make sure you don\'t repeat IDs!')
            self.title.setToolTip('<b>Title:</b><br>Changes the text which will appear on the top of the message box')
            self.text.setToolTip('<b>Text:</b><br>Changes the text which will appear inside the main portion of the message box')
        else:
            self.id.setToolTip('<b>ID:</b><br>Reggie等でメッセージボックスの文章を検索する際に使用する値です。同じIDを入力しないでください!')
            self.title.setToolTip('<b>タイトル:</b><br>メッセージボックス上部のタイトルを変更します。')
            self.text.setToolTip('<b>テキスト:</b><br>メッセージボックス内の文章を変更します。')

        # Set up handlers
        self.id.valueChanged.connect(self.HandleIdChanged)
        self.title.textChanged.connect(self.HandleTitleChanged)
        self.text.textChanged.connect(self.HandleTextChanged)

        # Set up a layout
        if MSLANG == 'English':
            L = QtWidgets.QFormLayout()
            L.addRow('ID:', self.id)
            L.addRow('Title:', self.title)
            L.addRow('Text:', self.text)
            self.setLayout(L)
        else:
            L = QtWidgets.QFormLayout()
            L.addRow('ID:', self.id)
            L.addRow('タイトル:', self.title)
            L.addRow('テキスト:', self.text)
            self.setLayout(L)

        # Clear everything
        self.clear()

    def clear(self):
        """Clears all data from the MessageEditor"""
        self.msg = None

        # ID
        self.id.setEnabled(False)
        self.id.setValue(0)

        # Title
        self.title.setEnabled(False)
        self.title.setText('')

        # Text
        self.text.setEnabled(False)
        self.text.setPlainText('')

    def setMessage(self, msg):
        """Sets the current message to msg"""
        self.msg = msg

        # ID
        self.id.setEnabled(True)
        self.id.setValue(msg.id)

        # Title
        self.title.setEnabled(True)
        self.title.setText(str(msg.title))

        # Text
        self.text.setEnabled(True)
        self.text.setPlainText(str(msg.text))

    def HandleIdChanged(self):
        """Handles changes to the ID box"""
        if self.msg == None: return
        self.msg.id = self.id.value()
        self.dataChanged.emit()

    def HandleTitleChanged(self):
        """Handles changes to the title box"""
        if self.msg == None: return
        self.msg.title = str(self.title.text())
        self.dataChanged.emit()

    def HandleTextChanged(self):
        """Handles changes to the text box"""
        if self.msg == None: return
        self.msg.text = str(self.text.toPlainText())
        self.dataChanged.emit()


# Check Duplicate IDs dialog
class CheckDuplicateIDsDlg(QtWidgets.QDialog):
    """Dialog which checks for duplicate message IDs"""
    def __init__(self, file):
        """Initialises the dialog"""
        QtWidgets.QDialog.__init__(self)

        # Find duplicates
        IDs = []
        for msg in file.Messages:
            i = msg.id
            counter = None
            found = False
            for acounter in IDs:
                if acounter[0] == i:
                    counter = acounter
                    found = True

            if found == True:
                counter[1] += 1
            else:
                counter = [i, 1]
                IDs.append(counter)

        # Sort it
        IDs = sorted(IDs, key=lambda msg: msg[0])

        # Make a header label
        if MSLANG == 'English':
            head = QtWidgets.QLabel('The file has been scanned. Problems are listed below:')
        else:
            head = QtWidgets.QLabel('ファイルをスキャンしました。以下は問題個所の一覧です:')
        # Make a list widget
        listW = QtWidgets.QListWidget()
        listW.setSelectionMode(listW.NoSelection)
        for id in IDs:
            if id[1] > 1: listW.addItem('There are %d messages with ID %d' % (id[1], id[0]))

        if VMode == 'Dark':
            self.setStyleSheet(StyleSheet)
        else:
            pass

        # Make the buttonbox
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        # Make a layout
        L = QtWidgets.QVBoxLayout()
        L.addWidget(head)
        L.addWidget(listW)
        L.addWidget(buttonBox)
        self.setLayout(L)
    

################################################################
################################################################
################################################################
######################### Main Window ##########################

class MainWindow(QtWidgets.QMainWindow):
    """Main window"""
    def __init__(self):
        """Initialises the window"""
        QtWidgets.QMainWindow.__init__(self)
        self.fp = None # file path

        # Create the viewer
        self.view = MessageViewer()
        self.setCentralWidget(self.view)

        # Create the menubar and a few actions
        self.CreateMenubar()

        # Set window title and show the window
        self.setWindowTitle('Newer Messages Editor 1.3-mod')
        self.show()

        if VMode == 'Dark':
            self.setStyleSheet(StyleSheet)
        else:
            pass

    def CreateMenubar(self):
        """Sets up the menubar"""
        m = self.menuBar()

        # File Menu
        if MSLANG == 'English':
            f = m.addMenu('&File')

            newAct = f.addAction('New File...')
            newAct.setShortcut('Ctrl+N')
            newAct.triggered.connect(self.HandleNew)

            openAct = f.addAction('Open File...')
            openAct.setShortcut('Ctrl+O')
            openAct.triggered.connect(self.HandleOpen)

            self.saveAct = f.addAction('Save File')
            self.saveAct.setShortcut('Ctrl+S')
            self.saveAct.triggered.connect(self.HandleSave)
            self.saveAct.setEnabled(False)

            self.saveAsAct = f.addAction('Save File As...')
            self.saveAsAct.setShortcut('Ctrl+Shift+S')
            self.saveAsAct.triggered.connect(self.HandleSaveAs)
            self.saveAsAct.setEnabled(False)

            f.addSeparator()

            self.checkAct = f.addAction('Check for Duplicate IDs...')
            self.checkAct.setShortcut('Ctrl+I')
            self.checkAct.triggered.connect(self.HandleCheckIDs)
            self.checkAct.setEnabled(False)

            f.addSeparator()

            exitAct = f.addAction('Exit')
            exitAct.setShortcut('Ctrl+Q')
            exitAct.triggered.connect(self.HandleExit)

        else:
            f = m.addMenu('&ファイル')

            newAct = f.addAction('新規作成')
            newAct.setShortcut('Ctrl+N')
            newAct.triggered.connect(self.HandleNew)

            openAct = f.addAction('ファイルを開く')
            openAct.setShortcut('Ctrl+O')
            openAct.triggered.connect(self.HandleOpen)

            self.saveAct = f.addAction('保存')
            self.saveAct.setShortcut('Ctrl+S')
            self.saveAct.triggered.connect(self.HandleSave)
            self.saveAct.setEnabled(False)

            self.saveAsAct = f.addAction('名前を付けて保存')
            self.saveAsAct.setShortcut('Ctrl+Shift+S')
            self.saveAsAct.triggered.connect(self.HandleSaveAs)
            self.saveAsAct.setEnabled(False)

            f.addSeparator()

            self.checkAct = f.addAction('Duplicate IDを調べる')
            self.checkAct.setShortcut('Ctrl+I')
            self.checkAct.triggered.connect(self.HandleCheckIDs)
            self.checkAct.setEnabled(False)

            f.addSeparator()

            exitAct = f.addAction('閉じる')
            exitAct.setShortcut('Ctrl+Q')
            exitAct.triggered.connect(self.HandleExit)

        # Setting Menu
        if MSLANG == 'English':
            s = m.addMenu('&Setting')

            aboutAct = s.addAction('Language')
            aboutAct.setShortcut('Ctrl+L')
            aboutAct.triggered.connect(self.HandleLS)

            aboutAct = s.addAction('Appearance')
            aboutAct.triggered.connect(self.HandleVS)

        else:
            s = m.addMenu('&設定')

            aboutAct = s.addAction('言語')
            aboutAct.setShortcut('Ctrl+L')
            aboutAct.triggered.connect(self.HandleLS)

            aboutAct = s.addAction('外観モード')
            aboutAct.triggered.connect(self.HandleVS)

        # Help Menu
        if MSLANG == 'English':
            h = m.addMenu('&Help')

            aboutAct = h.addAction('About...')
            aboutAct.setShortcut('Ctrl+H')
            aboutAct.triggered.connect(self.HandleAbout)
        else:
            h = m.addMenu('&ヘルプ')

            aboutAct = h.addAction('このソフトについて')
            aboutAct.setShortcut('Ctrl+H')
            aboutAct.triggered.connect(self.HandleAbout)


    def HandleNew(self):
        """Handles creating a new file"""
        f = MessagesBin()
        self.view.setFile(f)
        self.saveAsAct.setEnabled(True)
        self.checkAct.setEnabled(True)

    def HandleOpen(self):
        """Handles file opening"""
        if MSLANG == 'English':
            fp = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', '', 'Binary Files (*.bin);;All Files (*)')[0]
        else:
            fp = QtWidgets.QFileDialog.getOpenFileName(self, 'ファイルを開く', '', 'バイナリファイル(*.bin);;すべてのファイル(*)')[0]            
        if fp == '': return
        self.fp = fp

        # Open the file
        file = open(fp, 'rb')
        data = file.read()
        file.close()

        if sys.version[0] == '2': # Py2
            # convert the str to a list
            new = []
            for char in data: new.append(ord(char))
            data = new
        
        M = MessagesBin(data)

        # Update the viewer with this data
        self.view.setFile(M)

        # Enable saving
        self.saveAct.setEnabled(True)
        self.saveAsAct.setEnabled(True)
        self.checkAct.setEnabled(True)

    def HandleSave(self):
        """Handles file saving"""
        data = self.view.saveFile()

        # Save to the file
        file = open(self.fp, 'wb')
        file.write(data)
        file.close()

    def HandleSaveAs(self):
        """Handles saving to a new file"""
        if MSLANG == 'English':
            fp = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', '', 'Binary Files (*.bin);;All Files (*)')[0]
        else:
            fp = QtWidgets.QFileDialog.getSaveFileName(self, 'ファイルを保存', '', 'バイナリファイル(*.bin);;すべてのファイル(*)')[0]
        if fp == '': return
        self.fp = fp

        # Save it
        self.HandleSave()

        # Enable saving
        self.saveAct.setEnabled(True)

    def HandleCheckIDs(self):
        """Handles checking for duplicate Msg IDs"""
        dlg = CheckDuplicateIDsDlg(self.view.file)
        dlg.exec_() # we don't need to do anything else

    def HandleExit(self):
        """Exits"""
        raise SystemExit

# Added by wakanameko

    def HandleEN(self):
        if MSLANG == 'Japanese':
            if VMode == 'Light':
                DFile = open(STpath, 'w')
                DFile.write("ENL")
                DFile.close()
            else:
                DFile = open(STpath, 'w')
                DFile.write("END")
                DFile.close()
        else:
            pass

    def HandleJP(self):
        if MSLANG == 'English':
            if VMode == 'Light':
                DFile = open(STpath, 'w')
                DFile.write("JPL")
                DFile.close()
            else:
                DFile = open(STpath, 'w')
                DFile.write("JPD")
                DFile.close()
        else:
            pass

    def HandleLS(self):
        """Shows the About dialog"""
        # Add Buttons
        LangWindow = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        #LangWindow = QtWidgets.QMdiSubWindow
        if MSLANG == 'English':
            self.ENTip = QtWidgets.QPushButton('English')
            self.ENTip.setToolTip('<b>English:</b><br>Change language to English.')
            self.ENTip.setHidden(False) 
            self.JPTip = QtWidgets.QPushButton('Japanese')
            self.JPTip.setToolTip('<b>Japanese:</b><br>Change language to Japanese.')
        else:
            self.ENTip = QtWidgets.QPushButton('英語')
            self.ENTip.setToolTip('<b>英語:</b><br>言語を英語に変更します。')
            self.ENTip.setHidden(False) 
            self.JPTip = QtWidgets.QPushButton('日本語')
            self.JPTip.setToolTip('<b>日本語:</b><br>言語を日本語に変更します。')
        self.JPTip.setHidden(False) 
        # layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(LangWindow)
        layout = QtWidgets.QHBoxLayout() 
        layout.addWidget(self.ENTip) 
        layout.addWidget(self.JPTip) 

        # Click Buttons
        self.ENTip.clicked.connect(self.HandleEN)
        self.JPTip.clicked.connect(self.HandleJP)

        dlg = QtWidgets.QDialog(self)
        if MSLANG == 'English':
            dlg.setWindowTitle('Select Language')
        else:
            dlg.setWindowTitle('言語選択')
        dlg.setLayout(layout)
        dlg.setModal(True)
        dlg.setMinimumWidth(384)
                
        if VMode == 'Dark':
            self.setStyleSheet(StyleSheet)
        else:
            pass

        dlg.exec_()

    def HandleWH(self):
        if VMode == 'Dark':
            if MSLANG == 'English':
                DFile = open(STpath, 'w')
                DFile.write("ENL")
                DFile.close()
            else:
                DFile = open(STpath, 'w')
                DFile.write("JPL")
                DFile.close()
        else:
            pass

    def HandleDR(self):
        if VMode == 'Light':
            if MSLANG == 'English':
                DFile = open(STpath, 'w')
                DFile.write("END")
                DFile.close()
            else:
                DFile = open(STpath, 'w')
                DFile.write("JPD")
                DFile.close()
        else:
            pass

    def HandleVS(self):
        """Shows the About dialog"""
        # Add Buttons
        VSWindow = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        #VSWindow = QtWidgets.QMdiSubWindow
        if MSLANG == 'English':
            self.WHTip = QtWidgets.QPushButton('Light Mode')
            self.WHTip.setToolTip('<b>Light Mode:</b><br>Change the appearance to White mode.')
            self.WHTip.setHidden(False) 
            self.DRTip = QtWidgets.QPushButton('Dark Mode')
            self.DRTip.setToolTip('<b>Dark Mode:</b><br>Change the appearance to dark mode.')
        else:
            self.WHTip = QtWidgets.QPushButton('ライトモード')
            self.WHTip.setToolTip('<b>ライトモード:</b><br>外観をライトモードに変更します。')
            self.WHTip.setHidden(False) 
            self.DRTip = QtWidgets.QPushButton('ダークモード')
            self.DRTip.setToolTip('<b>ダークモード:</b><br>外観をダークモードに変更します。')
        self.DRTip.setHidden(False) 
        # layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(VSWindow)
        layout = QtWidgets.QHBoxLayout() 
        layout.addWidget(self.WHTip) 
        layout.addWidget(self.DRTip) 

        # Click Buttons
        self.WHTip.clicked.connect(self.HandleWH)
        self.DRTip.clicked.connect(self.HandleDR)

        dlg = QtWidgets.QDialog(self)
        if MSLANG == 'English':
            dlg.setWindowTitle('Appearance')
        else:
            dlg.setWindowTitle('外観モード')
        dlg.setLayout(layout)
        dlg.setModal(True)
        dlg.setMinimumWidth(384)
                
        if VMode == 'Dark':
            self.setStyleSheet(StyleSheet)
        else:
            pass

        dlg.exec_()

# finish

    def HandleAbout(self):
        """Shows the About dialog"""
        try: readme = open('readme.md', 'r').read()
        except: readme = 'Newer Messages Editor %s by RoadrunnerWMC\nmod by @wakanameko2\n(No readme.md found!)\nLicensed under GPL 3' % version

        txtedit = QtWidgets.QPlainTextEdit(readme)
        txtedit.setReadOnly(True)

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(txtedit)
        layout.addWidget(buttonBox)
        
        dlg = QtWidgets.QDialog(self)
        if MSLANG == 'English':
            dlg.setWindowTitle('About Newer Messages Editor')
        else:
            dlg.setWindowTitle('Newer Messages Editorについて')
        dlg.setLayout(layout)
        dlg.setModal(True)
        dlg.setMinimumWidth(384)
        
        if VMode == 'Dark':
            self.setStyleSheet(StyleSheet)
        else:
            pass

        buttonBox.accepted.connect(dlg.accept)

        dlg.exec_()


################################################################
################################################################
################################################################
############################ Main() ############################


# Main function
def main():
    """Main startup function"""
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
main()
