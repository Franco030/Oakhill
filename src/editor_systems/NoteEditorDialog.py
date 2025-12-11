import json
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
    QTextEdit, QLineEdit, QPushButton, QLabel, 
    QMessageBox, QInputDialog, QTabWidget, QWidget, 
    QSplitter, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont

class NoteLimitHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
    
        self.MAX_CHARS_PER_LINE = 39
        self.MAX_LINES_PER_PAGE = 14 
        
        self.error_format = QTextCharFormat()
        self.error_format.setForeground(QColor("#FF0000"))
        self.error_format.setFontWeight(QFont.Bold)

        self.page_break_format = QTextCharFormat()
        self.page_break_format.setForeground(QColor("#FFFF00"))
        self.page_break_format.setFontWeight(QFont.Bold)

    def highlightBlock(self, text):
        if len(text) > self.MAX_CHARS_PER_LINE:
            self.setFormat(self.MAX_CHARS_PER_LINE, len(text) - self.MAX_CHARS_PER_LINE, self.error_format)

        
        previous_line_count = self.previousBlockState()
        if previous_line_count == -1: previous_line_count = 0
        
        current_line_count = previous_line_count + 1

        if current_line_count > self.MAX_LINES_PER_PAGE:
            self.setFormat(0, len(text), self.error_format)

        if "[P]" in text:
            index = text.find("[P]")
            while index >= 0:
                self.setFormat(index, 3, self.page_break_format)
                index = text.find("[P]", index + 3)
            
            self.setCurrentBlockState(0) 
        else:
            self.setCurrentBlockState(current_line_count)

        

class NoteEditorDialog(QDialog):
    def __init__(self, base_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Notes manager")
        self.resize(1000, 700)
        
        self.base_path = base_path
        self.notes_file = os.path.join(self.base_path, "data/notes.json")
        self.notes_data = {}
        self.current_note_id = None
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for Note ID")
        self.search_bar.textChanged.connect(self.filter_list)
        left_layout.addWidget(self.search_bar)
        
        self.list_notes = QListWidget()
        self.list_notes.itemSelectionChanged.connect(self.on_note_selected)
        left_layout.addWidget(self.list_notes)
        
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("+ New note")
        self.btn_add.clicked.connect(self.add_note)
        self.btn_delete = QPushButton("- Delete note")
        self.btn_delete.clicked.connect(self.delete_note)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)
        left_layout.addLayout(btn_layout)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.lbl_id = QLabel("Select a note to edit")
        right_layout.addWidget(self.lbl_id)
        
        self.tabs = QTabWidget()

        font = QFont("Consolas", 10)
    
        self.edit_en = QTextEdit()
        self.tabs.addTab(self.edit_en, "English (EN)")
        self.highlighter_en = NoteLimitHighlighter(self.edit_en.document())
        self.edit_en.setFont(font)
        
        self.edit_es = QTextEdit()
        self.highlighter_es = NoteLimitHighlighter(self.edit_es.document())
        self.edit_es.setFont(font)
        self.tabs.addTab(self.edit_es, "Español (ES)")
        
        right_layout.addWidget(self.tabs)
        
        tools_layout = QHBoxLayout()
        self.btn_insert_page = QPushButton("Insert a new page [P]")
        self.btn_insert_page.setToolTip("Inserts the text '[P]' in the cursor's position")
        self.btn_insert_page.clicked.connect(self.insert_page_break)
        tools_layout.addWidget(self.btn_insert_page)
        tools_layout.addStretch()
        right_layout.addLayout(tools_layout)
        
        self.btn_save = QPushButton("Save changes (JSON)")
        self.btn_save.clicked.connect(self.save_data)
        right_layout.addWidget(self.btn_save)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(1, 2)
        main_layout.addWidget(splitter)

        self.enable_editing(False)

    def enable_editing(self, enabled):
        self.tabs.setEnabled(enabled)
        self.btn_insert_page.setEnabled(enabled)
        self.btn_delete.setEnabled(enabled)

    def load_data(self):
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, "r", encoding="utf-8") as f:
                    self.notes_data = json.load(f)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading JSON: {e}")
                self.notes_data = {}
        
        self.refresh_list()

    def refresh_list(self):
        self.list_notes.clear()
        search = self.search_bar.text().lower()
        
        for note_id in sorted(self.notes_data.keys()):
            if search and search not in note_id.lower():
                continue
            self.list_notes.addItem(note_id)

    def filter_list(self):
        self.refresh_list()

    def on_note_selected(self):
        items = self.list_notes.selectedItems()
        if not items:
            self.current_note_id = None
            self.lbl_id.setText("Select a note to edit")
            self.edit_es.clear()
            self.edit_en.clear()
            self.enable_editing(False)
            return

        note_id = items[0].text()
        self.current_note_id = note_id
        self.lbl_id.setText(f"Editing: {note_id}")
        self.enable_editing(True)
        
        data = self.notes_data[note_id]
        content = data.get("content", {})
        
        self.edit_es.setPlainText(content.get("es", ""))
        self.edit_en.setPlainText(content.get("en", ""))

    def add_note(self):
        new_id, ok = QInputDialog.getText(self, "New note", "Note ID:")
        if ok and new_id:
            new_id = new_id.strip() 
            
            if new_id in self.notes_data:
                QMessageBox.warning(self, "Error", "ID already exists")
                return
            
            self.notes_data[new_id] = {
                "content": { "es": "", "en": "" }
            }
            
            self.save_data() 
            self.refresh_list()
            
            items = self.list_notes.findItems(new_id, Qt.MatchExactly)
            if items:
                self.list_notes.setCurrentItem(items[0])

    def delete_note(self):
        if not self.current_note_id: return
        
        res = QMessageBox.question(self, "Confirm", f"Delete '{self.current_note_id}'?", QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.Yes:
            del self.notes_data[self.current_note_id]
            
            self.current_note_id = None
            self.lbl_id.setText("Select a note to edit")
            self.edit_es.clear()
            self.edit_en.clear()
            self.enable_editing(False)

            self.save_data()
            self.refresh_list()

    def insert_page_break(self):
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, QTextEdit):
            current_widget.insertPlainText("[P]")
            current_widget.setFocus()

    def save_data(self):
        if self.current_note_id:
            self.notes_data[self.current_note_id]["content"]["es"] = self.edit_es.toPlainText()
            self.notes_data[self.current_note_id]["content"]["en"] = self.edit_en.toPlainText()
        
        try:
            with open(self.notes_file, "w", encoding="utf-8") as f:
                json.dump(self.notes_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Couldn't save: {e}")