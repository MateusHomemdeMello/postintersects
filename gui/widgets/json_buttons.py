"""
Este módulo define o widget JSONButtons, um componente com dois botões:
- Importar JSON: carrega um dicionário de credenciais de um arquivo
- Exportar JSON: salva os dados atuais em um arquivo JSON

Este componente interage diretamente com um ConnectionForm e opcionalmente
um logger visual.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog, QMessageBox
import json
import os


class JSONButtons(QWidget):
    def __init__(self, connection_form, logger=None, parent=None):
        """
        Parâmetros:
        - connection_form: instância de ConnectionForm
        - logger: instância de Logger (opcional)
        """
        super().__init__(parent)
        self.connection_form = connection_form
        self.logger = logger
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.import_btn = QPushButton("Importar JSON")
        self.import_btn.clicked.connect(self._importar_json)

        self.export_btn = QPushButton("Exportar JSON")
        self.export_btn.clicked.connect(self._exportar_json)

        layout.addWidget(self.import_btn)
        layout.addWidget(self.export_btn)
        layout.addStretch()

        self.setLayout(layout)

    def _importar_json(self):
        caminho, _ = QFileDialog.getOpenFileName(self, "Selecionar arquivo JSON", "", "JSON (*.json)")
        if not caminho:
            return

        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)

            self.connection_form.set_data(dados)
            if self.logger:
                self.logger.log(f"[Import] Credenciais importadas de: {os.path.basename(caminho)}")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao importar JSON:\n{e}")
            if self.logger:
                self.logger.log(f"[Erro] Falha ao importar JSON: {e}")

    def _exportar_json(self):
        dados = self.connection_form.get_data()

        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar JSON", "", "JSON (*.json)")
        if not caminho:
            return

        try:
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)

            if self.logger:
                self.logger.log(f"[Export] Credenciais exportadas para: {caminho}")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar JSON:\n{e}")
            if self.logger:
                self.logger.log(f"[Erro] Falha ao exportar JSON: {e}")
