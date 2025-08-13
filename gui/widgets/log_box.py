"""
Este módulo define a classe LogBox, um widget baseado em QTextEdit para exibir
mensagens de log da aplicação de forma legível, com rolagem automática e fonte
monoespaçada.
"""

from PyQt6.QtWidgets import QTextEdit


class LogBox(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMinimumHeight(110)
        self.setStyleSheet("""
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 10pt;
        """)

    def append_log(self, message: str):
        """
        Adiciona uma nova linha de log e rola automaticamente até o final.
        """
        self.append(message)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
