"""
Este módulo define a classe Logger, um utilitário que permite enviar logs
simultaneamente para o console (stdout) e, opcionalmente, para um componente
de interface gráfica como QTextEdit.

É útil para manter rastreamento de ações tanto para o usuário quanto para debug.
"""

from PyQt6.QtWidgets import QTextEdit


class Logger:
    def __init__(self, widget: QTextEdit = None):
        """
        Inicializa o logger.

        Parâmetro:
        - widget: instância de QTextEdit (opcional), usada para exibir logs na interface.
        """
        self.widget = widget

    def log(self, message: str):
        """
        Registra uma mensagem no console e na interface, se aplicável.
        """
        print(message)
        if self.widget:
            self.widget.append(message)
            self.widget.verticalScrollBar().setValue(
                self.widget.verticalScrollBar().maximum()
            )

    def clear(self):
        """
        Limpa o conteúdo do widget de log (apenas se for um QTextEdit).
        """
        if self.widget:
            self.widget.clear()
