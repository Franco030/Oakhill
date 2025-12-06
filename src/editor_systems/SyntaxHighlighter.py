from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import QRegularExpression

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._highlighting_rules = []

        key_format = QTextCharFormat()
        key_format.setForeground(QColor("#569CD6"))
        key_format.setFontWeight(QFont.Bold)
        self._highlighting_rules.append((QRegularExpression(r"\b[\w]+(?=\s*=)"), key_format))

        # quote_format = QTextCharFormat()
        # quote_format.setForeground(QColor("#CE9178"))
        # self._highlighting_rules.append((QRegularExpression(r"\"[^\"]*\""), quote_format))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self._highlighting_rules.append((QRegularExpression(r"\b-?[0-9]+(\.[0-9]+)?\b"), number_format))

        bool_format = QTextCharFormat()
        bool_format.setForeground(QColor("#C586C0"))
        self._highlighting_rules.append((QRegularExpression(r"\b(true|false)\b"), bool_format))
        
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self._highlighting_rules.append((QRegularExpression(r"#.*"), comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self._highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)