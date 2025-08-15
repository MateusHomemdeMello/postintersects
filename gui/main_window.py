"""
Este módulo define a classe MainWindow, que representa a janela principal da aplicação.
Ela organiza a interface em abas, conecta os componentes visuais e prepara o terreno
para a lógica de interação com banco, arquivos e operações espaciais.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTabWidget
from PyQt6.QtCore import Qt

from gui.tabs.input_tab import InputTab
from gui.tabs.results_tab import ResultsTab


class MainWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PostIntersect - Consultas de interseção Espacial no PostGIS")
        self.resize(600, 600)
        self.setMinimumWidth(520)

        # Define botões da janela (min/max/fechar)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        self._setup_ui()

    def _setup_ui(self):
        """
        Monta o layout principal da janela, com as abas.
        """
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Criação das abas (composição)
        self.input_tab = InputTab(self)
        self.results_tab = ResultsTab(self)

        self.tabs.addTab(self.input_tab, "Entrada")
        self.tabs.addTab(self.results_tab, "Visualização")

        # Por padrão, oculta a aba de resultados até que seja necessário
        self.tabs.setTabVisible(1, False)

    def mostrar_aba_resultados(self):
        """
        Torna a aba de visualização visível e ativa.
        """
        self.tabs.setTabVisible(1, True)
        self.tabs.setCurrentIndex(1)
