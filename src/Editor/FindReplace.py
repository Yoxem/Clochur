import sys
from PyQt5.QtWidgets import *
from PyQt5.Qsci import QsciScintilla

class FindReplace(QDialog):
    def __init__(self, parent):
        super(QDialog, self).__init__()

        self.parent = parent
        
        self.find_label = QLabel("Find:")
        self.find_line_edit = QLineEdit()
        self.find_label.setBuddy(self.find_line_edit)
        
        self.replace_label = QLabel("Replace:")
        self.replace_line_edit = QLineEdit()
        self.replace_label.setBuddy(self.replace_line_edit)   


        self.top_grid_layout = QGridLayout()

        self.top_grid_layout.addWidget(self.find_label,0,0)
        self.top_grid_layout.addWidget(self.find_line_edit,0,1)

        self.top_grid_layout.addWidget(self.replace_label,1,0)
        self.top_grid_layout.addWidget(self.replace_line_edit,1,1)

        self.regex_checkbox = QCheckBox('Using regex',self)
        self.case_sensitive_checkbox = QCheckBox('Case sensitive',self)
        self.match_whole_word_checkbox = QCheckBox('Match whole word',self)


        self.find_next_botton = QPushButton("Find next")
        self.find_prev_botton = QPushButton("Find prev.")
        self.replace_botton = QPushButton("Replace")
        self.replace_all_botton = QPushButton("Replace all")


        self.botton_layout = QHBoxLayout()
        self.botton_layout.addWidget(self.find_next_botton)
        self.botton_layout.addWidget(self.find_prev_botton)
        self.botton_layout.addWidget(self.replace_botton)
        self.botton_layout.addWidget(self.replace_all_botton)


        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.top_grid_layout)
        self.main_layout.addWidget(self.regex_checkbox)
        self.main_layout.addWidget(self.case_sensitive_checkbox)
        self.main_layout.addWidget(self.match_whole_word_checkbox)
        self.main_layout.addLayout(self.botton_layout)


        self.setLayout(self.main_layout)
        
        self.setWindowTitle("Find and replace")

        self.set_action()
    
    def set_action(self):
        self.find_next_botton.clicked.connect(self.find_next_call)
        self.find_prev_botton.clicked.connect(self.find_prev_call)
        self.replace_botton.clicked.connect(self.replace_call)
        self.replace_all_botton.clicked.connect(self.replace_all_call)

    def find_next_call(self):
        is_first_checked = True

        is_regex = False
        is_case_sensitive = False
        is_matched_whole_word = False

        is_wrap_search = True

        text = self.find_line_edit.text()
        if self.regex_checkbox.isChecked() == True:
            is_regex = True

        if self.case_sensitive_checkbox.isChecked() == True:
            is_case_sensitive = True

        if self.match_whole_word_checkbox.isChecked() == True:
            is_matched_whole_word = True

        if is_first_checked == True:
            self.parent.editor.findFirst(text, is_regex, is_case_sensitive, is_matched_whole_word, is_wrap_search)
            is_first_checked = False
        else:
            self.parent.editor.findNext()

    def find_prev_call(self):
        total_line_number = self.parent.editor.SendScintilla(QsciScintilla.SCI_GETLINECOUNT)

        is_first_checked = True

        is_regex = False
        is_case_sensitive = False
        is_matched_whole_word = False

        is_wrap_search = True

        text = self.find_line_edit.text()
        if self.regex_checkbox.isChecked() == True:
            is_regex = True

        if self.case_sensitive_checkbox.isChecked() == True:
            is_case_sensitive = True

        if self.match_whole_word_checkbox.isChecked() == True:
            is_matched_whole_word = True

        editor = self.parent.editor
        editor.findFirst(text, is_regex, is_case_sensitive, is_matched_whole_word, is_wrap_search, forward = False,
                        line = editor.getSelection()[0], index=editor.getSelection()[1])

    def replace_call(self):
        editor = self.parent.editor

        is_first_checked = True

        is_regex = False
        is_case_sensitive = False
        is_matched_whole_word = False

        is_wrap_search = True

        text = self.find_line_edit.text()
        if self.regex_checkbox.isChecked() == True:
            is_regex = True

        if self.case_sensitive_checkbox.isChecked() == True:
            is_case_sensitive = True

        if self.match_whole_word_checkbox.isChecked() == True:
            is_matched_whole_word = True

        text = self.find_line_edit.text()
        replacing_text = self.replace_line_edit.text()
        editor.replace(replacing_text)
    
    def replace_all_call(self):
        editor = self.parent.editor

        is_first_checked = True

        is_regex = False
        is_case_sensitive = False
        is_matched_whole_word = False

        is_wrap_search = True

        text = self.find_line_edit.text()
        replacing_text = self.replace_line_edit.text()
        if self.regex_checkbox.isChecked() == True:
            is_regex = True

        if self.case_sensitive_checkbox.isChecked() == True:
            is_case_sensitive = True

        if self.match_whole_word_checkbox.isChecked() == True:
            is_matched_whole_word = True

        while editor.findFirst(text, is_regex, is_case_sensitive, is_matched_whole_word, is_wrap_search,
                                            line=editor.getSelection()[2], index=editor.getSelection()[3], forward = True):
            editor.replace(replacing_text)

    

        






