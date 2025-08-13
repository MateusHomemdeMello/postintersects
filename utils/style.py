"""
Este módulo define o estilo visual escuro (dark theme) para a aplicação Qt,
centralizando as regras de aparência para facilitar a manutenção e reutilização.
"""

DARK_STYLE = """
QWidget {
    background-color: #232629;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10.5pt;
}
QLineEdit, QComboBox, QTreeWidget, QTabWidget, QTableWidget, QTextEdit {
    background-color: #31363b;
    color: #e0e0e0;
    border: 1px solid #444;
    border-radius: 4px;
}
QPushButton {
    background-color: #3daee9;
    color: #232629;
    border: none;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #6cc7f7;
}
QPushButton:pressed {
    background-color: #2d8abf;
}
QLabel {
    color: #e0e0e0;
}
QTabBar::tab {
    background: #31363b;
    color: #e0e0e0;
    padding: 8px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}
QTabBar::tab:selected {
    background: #3daee9;
    color: #232629;
}
QTreeWidget::item:selected {
    background: #3daee9;
    color: #232629;
}
QMessageBox {
    background-color: #232629;
    color: #e0e0e0;
}
"""
