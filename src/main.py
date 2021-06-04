#!/usr/bin/env python3
#-*-coding:utf-8-*-

import json
import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtWidgets import *
from PyQt5.Qsci import QsciScintilla

import qrc_resources
from EditorOther import FindReplace, CustomQsciEditor

filename = None


dirname = os.path.abspath(os.path.dirname(__file__)) #os.path.dirname('__file__')
PDFJS = os.path.join(dirname, '../thirdparty/pdfjs/web/viewer.html')
PDF = os.path.join(dirname, 'example.pdf')



'''Widget for PDF file viewer'''
class PDFJSWidget(QtWebEngineWidgets.QWebEngineView):
    def __init__(self):
        super(PDFJSWidget, self).__init__()
        self.load(QUrl.fromUserInput("file://%s?file=file://%s"  % (PDFJS, PDF)))
        print((dirname,PDFJS, PDF))




class Window(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.file = None
        self.filename = None
        self.font_family = 'Noto Sans Mono'
        self.font_size = 11

        self.tmp_folder = '/tmp'
        self.tmp_file = 'clochur_tmp.json'
        self.untitled_id = None

        self.opened_file_dirname = os.path.expanduser("~")

        self._createActions()
        self._createMenuBar()
        self._createEditToolBar()
        self._createFormatToolBar()

        self.setWindowIcon(QIcon(':logo.svg'))

    def _createActions(self):
        self.new_action = QAction(QIcon(":new.svg"), "&New", self)
        self.new_action.setShortcut('Ctrl+N')
        self.new_action.triggered.connect(self.new_call)

        self.open_action = QAction(QIcon(":open.svg"), "&Open...", self)
        self.open_action.setShortcut('Ctrl+O')
        self.open_action.triggered.connect(self.open_call)

        self.save_action = QAction(QIcon(":save.svg"), "&Save", self)
        self.save_action.setShortcut('Ctrl+S')
        self.save_action.triggered.connect(self.save_call)

        self.save_as_action = QAction(QIcon(":save-as.svg"), "Save as...", self)
        self.save_as_action.triggered.connect(self.save_as_call)

        self.exit_action = QAction("&Exit", self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.triggered.connect(self.exit_call)

        self.undo_action = QAction(QIcon(":undo.svg"), "&Undo", self)
        self.undo_action.setShortcut('Ctrl+Z')
        self.undo_action.triggered.connect(self.undo_call)

        self.redo_action = QAction(QIcon(":redo.svg"), "&Redo", self)
        self.redo_action.setShortcut('Ctrl+Y')
        self.redo_action.triggered.connect(self.redo_call)

        self.copy_action = QAction(QIcon(":copy.svg"), "&Copy", self)
        self.copy_action.setShortcut('Ctrl+C')
        self.copy_action.triggered.connect(self.copy_call)

        self.paste_action = QAction(QIcon(":paste.svg"), "&Paste", self)
        self.paste_action.setShortcut('Ctrl+V')
        self.paste_action.triggered.connect(self.paste_call)

        self.cut_action = QAction(QIcon(":cut.svg"), "C&ut", self)
        self.cut_action.setShortcut('Ctrl+X')
        self.cut_action.triggered.connect(self.cut_call)

        self.find_and_replace_action = QAction(QIcon(":find-replace.svg"), "&Find and replace" , self)
        self.find_and_replace_action.setShortcut('Ctrl+F')
        self.find_and_replace_action.triggered.connect(self.find_and_replace_call)

        self.select_all_action = QAction( "Select &All" , self)
        self.select_all_action.setShortcut('Ctrl+A')
        self.select_all_action.triggered.connect(self.select_all_call)


        self.convert_action = QAction(QIcon(":convert.svg"), "Con&vert", self)

        self.about_action = QAction("&About", self)
        self.about_action.triggered.connect(self.about_call)       

        self.bold_action = QAction(QIcon(":text-bold.svg"), "&Bold", self)
        self.italic_action = QAction(QIcon(":text-italic.svg"), "&Italic", self)
        self.strike_action = QAction(QIcon(":text-strikethrough.svg"), "Stri&ke", self)
        self.underline_action = QAction(QIcon(":text-underline.svg"), "&Underline", self)

    def _createMenuBar(self):
        menuBar = QMenuBar(self)
        self.setMenuBar(menuBar)
        file_menu = menuBar.addMenu("&File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addAction(self.exit_action)

        edit_menu = menuBar.addMenu("&Edit")

        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)

        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_action)
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)


        edit_menu.addSeparator()

        edit_menu.addAction(self.select_all_action)    
        
        edit_menu.addSeparator()

        edit_menu.addAction(self.find_and_replace_action)    



        edit_menu.addAction(self.convert_action)



        format_menu = menuBar.addMenu("&Format")
        format_menu.addAction(self.bold_action)
        format_menu.addAction(self.italic_action)
        format_menu.addAction(self.strike_action)
        format_menu.addAction(self.underline_action)

        help_menu = menuBar.addMenu("&Help")
        help_menu.addAction(self.about_action)

    def closeEvent(self, event):
        self.exit_call()
        event.ignore()

    def new_call(self):
        os.system('clochur')

    def open_call(self):
        file_path = QFileDialog.getOpenFileName(self, 'Open file...', self.opened_file_dirname, "CLC typesetting format (*.clc)")
        if file_path[0] != '':
            self.filename = os.path.basename(file_path[0])
            self.opened_file_dirname = os.path.dirname(file_path[0])
            self.file = open(file_path[0], 'r', encoding='utf-8')
            editor.setText(self.file.read())
            self.file.close()



    def save_call(self):
        if self.filename == None:
            self.save_as_call()

            self.editor.setModified(False)
            
        else:
            self.file = open(os.path.join(self.opened_file_dirname,self.filename), 'w', encoding='utf-8')
            file_content = editor.text()
            self.file.write(file_content)
            self.file.close()
            
            self.editor.setModified(False)

    def removing_untitled_id(self):
            if self.untitled_id != None:
                with open(os.path.join(self.tmp_folder, self.tmp_file), 'r') as f:
                    data = json.load(f)
                    data["untitled"].remove(self.untitled_id)
                
                with open(os.path.join(self.tmp_folder, self.tmp_file), 'w') as f:
                    json.dump(data, f, indent=4)

    
    def save_as_call(self):
        file_path = QFileDialog.getSaveFileName(self, 'Save file as...', self.opened_file_dirname, "CLC typesetting format (*.clc)")
        if file_path[0] != '':
            self.filename = os.path.basename(file_path[0])
            self.opened_file_dirname = os.path.dirname(file_path[0])
            self.file = open(file_path[0], 'w', encoding='utf-8')
            file_content = editor.text()
            self.file.write(file_content)
            self.file.close()    

            self.editor.setModified(False)
            self.removing_untitled_id()


            self.setWindowTitle("Clochur - %s" % os.path.basename(file_path[0]))
        pass

    def exit_call(self):
        
        #reply = QMessageBox.question(self,'','Do You want to save this file? The text has been modified', QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.No)

        if self.editor.isModified():
            reply = QMessageBox.question(self,'','Do You want to save this file? The text has been modified', QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.No)
            if reply == QMessageBox.Yes:
                file_path = QFileDialog.getSaveFileName(self, 'Save file as...', opened_file_dirname, "CLC typesetting format (*.clc)")
                if file_path[0] != '':
                    self.file = open(file_path[0], 'w', encoding='utf-8')
                    file_content = editor.text()
                    self.file.write(file_content)
                    self.file.close()
                    self.removing_untitled_id()

            elif reply == QMessageBox.No:
                self.removing_untitled_id()
                app.exit()
            else:
                pass

        else:
            self.removing_untitled_id()
            app.exit()

    def undo_call(self):
        self.editor.undo()

    def redo_call(self):
        self.editor.redo()

    def copy_call(self):
        self.editor.copy()

    def paste_call(self):
        self.editor.paste()

    def cut_call(self):
        self.editor.cut()

    def find_and_replace_call(self):
        print(FindReplace)
        find_replace_dialog = FindReplace.FindReplace(self)
        type(find_replace_dialog)
        find_replace_dialog.exec_()

    def select_all_call(self):
        self.editor.selectAll()

    def about_call(self):
        about_content = '''A S-expression-like typesetting language powered by SILE engine with a simple text text editor.
http://yoxem.github.com
(c) 2021 Yoxem Chen <yoxem.tem98@nctu.edu.tw>'''

        self.about_dialog = QMessageBox.about(self, "About Clochur", about_content)
                

    def _createEditToolBar(self):
        editToolBar = QToolBar("Edit", self)
        editToolBar.toolButtonStyle = Qt.ToolButtonTextOnly
        self.addToolBar(Qt.TopToolBarArea, editToolBar)

        editToolBar.addAction(self.new_action)
        editToolBar.addAction(self.open_action)
        editToolBar.addAction(self.save_action)
        editToolBar.addAction(self.save_as_action)


        tool_bar_separator = editToolBar.addAction('|')
        tool_bar_separator.setEnabled(False)

        editToolBar.addAction(self.undo_action)
        editToolBar.addAction(self.redo_action)

        tool_bar_separator = editToolBar.addAction('|')
        tool_bar_separator.setEnabled(False)


        editToolBar.addAction(self.cut_action)
        editToolBar.addAction(self.copy_action)
        editToolBar.addAction(self.paste_action)

        tool_bar_separator = editToolBar.addAction('|')
        tool_bar_separator.setEnabled(False)

        editToolBar.addAction(self.convert_action)


    def _createFormatToolBar(self):
        self.addToolBarBreak() # Toolber newline
        formatToolBar = QToolBar("Format", self)
        formatToolBar.toolButtonStyle = Qt.ToolButtonTextOnly
        self.addToolBar(Qt.TopToolBarArea, formatToolBar)

        formatToolBar.addAction(self.bold_action)
        formatToolBar.addAction(self.italic_action)
        formatToolBar.addAction(self.strike_action)
        formatToolBar.addAction(self.underline_action)

        '''create font adder'''
        self.font_widget = QHBoxLayout()
        font_combo_box = QComboBox()
        font_database = QFontDatabase()
        font_families = font_database.families()

        font_combo_box.addItems(font_families)
        line_edit = font_combo_box.lineEdit()
        #line_edit.setFont(QFont(font_combo_box.currentText(),11))
        #print(type(font_combo_box.lineEdit()).__name__)

        font_button = QPushButton("Insert font")

        formatToolBar.addWidget(font_combo_box)
        formatToolBar.addWidget(font_button)

    def generate_untitled_title(self):
        json_file = os.path.join(self.tmp_folder, self.tmp_file)
        self.untitled_id = None
        if not os.path.isfile(json_file):
            with open(json_file, 'w') as f:
                content = '{"untitled" : [1]}'
                f.write(content)
                self.untitled_id = 1
        else:
            i = 1
            with open(json_file, 'r') as f:
                data = json.load(f)

                if data["untitled"] == []:
                    i = 1
                else:
                    while i in data["untitled"]:
                        i += 1
                data["untitled"].append(i)
                data["untitled"].sort()
            
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=4)
                self.untitled_id = i

        return "Untitled %d" % self.untitled_id
            








if __name__ == '__main__':
    app = QApplication([])
    window = Window()


    editor = CustomQsciEditor.CustomQsciEditor(window)
    editor.setMinimumWidth(200)
    #editor.resize(QSize(500, 2000))

    pdf_viewer = PDFJSWidget()
    pdf_viewer.setMinimumWidth(200)
    #pdf_viewer.resize(QSize(500, 2000))

    splitter = QSplitter(Qt.Horizontal)
    splitter.addWidget(editor)
    splitter.addWidget(pdf_viewer)
    splitter.setStretchFactor(0, 1)
    splitter.setSizes([500, 500])
    splitter.setChildrenCollapsible(False) # make the editor and the PDF reader uncollapsible.

    main_layout = QHBoxLayout()

    main_layout.addWidget(splitter)
    #main_layout.addWidget(pdf_viewer)


    window.editor = editor

    untitled_title = window.generate_untitled_title()

    if window.file != None:
        app.setApplicationName("Clochur - %s" % os.path.basename(window.file))
    else:
        app.setApplicationName("Clochur - %s" % untitled_title)

    main_widget = QWidget()
    main_widget.setLayout(main_layout)

    window.setCentralWidget(main_widget)
    window.show()

    sys.exit(app.exec_())