from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import QRegularExpression

COL_KEYWORD_ACTION = QColor("#ff7300")
COL_NUMBERS = QColor("#9DDB7B")
COL_BOOLEAN = QColor("#C773C0")
COL_ASSET_ID = QColor("#9089F0")
COL_NOTE_ID = QColor("D19A66")

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, asset_keywords=None):
        super().__init__(parent)
        self._highlighting_rules = []

        key_format = QTextCharFormat()
        key_format.setForeground(COL_KEYWORD_ACTION)
        key_format.setFontWeight(QFont.Bold)
        self._highlighting_rules.append((QRegularExpression(r"\b[\w]+(?=\s*=)"), key_format))

        # quote_format = QTextCharFormat()
        # quote_format.setForeground(QColor("#CE9178"))
        # self._highlighting_rules.append((QRegularExpression(r"\"[^\"]*\""), quote_format))

        number_format = QTextCharFormat()
        number_format.setForeground(COL_NUMBERS)
        self._highlighting_rules.append((QRegularExpression(r"\b-?[0-9]+(\.[0-9]+)?\b"), number_format))

        bool_format = QTextCharFormat()
        bool_format.setForeground(COL_BOOLEAN)
        self._highlighting_rules.append((QRegularExpression(r"\b(true|false)\b"), bool_format))
        
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self._highlighting_rules.append((QRegularExpression(r"#.*"), comment_format))

        if asset_keywords:
            asset_format = QTextCharFormat()
            asset_format.setForeground(COL_ASSET_ID)
            asset_format.setFontWeight(QFont.Bold)
            
            escaped_keywords = [QRegularExpression.escape(kw) for kw in asset_keywords]
            pattern_str = r"\b(" + "|".join(escaped_keywords) + r")\b"
            
            self._highlighting_rules.append((QRegularExpression(pattern_str), asset_format))

    def highlightBlock(self, text):
        for pattern, fmt in self._highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)