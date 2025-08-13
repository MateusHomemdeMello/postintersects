"""
Este módulo define a aba de resultados (ResultsTab), responsável por exibir os
resultados da interseção espacial com a AOI. Os dados são apresentados em um
QTreeWidget com opções de exportação para CSV e GeoPackage.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QHBoxLayout, QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from core.exporter.csv_exporter import CSVExporter
from core.exporter.gpkg_exporter import GPKGExporter
from utils.logger import Logger
from core.spatial.aoi import AOI


class ResultsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.conn = None
        self.resultados = []
        self.aoi_path = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Camada"])
        layout.addWidget(self.tree)

        # Botões de exportação
        btns = QHBoxLayout()
        self.export_diag_btn = QPushButton("Exportar Diagnóstico")
        self.export_diag_btn.clicked.connect(self._exportar_csv_diagnostico)
        btns.addWidget(self.export_diag_btn)


        self.export_gpkg_btn = QPushButton("Exportar GeoPackage")
        self.export_gpkg_btn.clicked.connect(self._exportar_gpkg)

        btns.addWidget(self.export_gpkg_btn)
        btns.addStretch()
        layout.addLayout(btns)

        self.logger = Logger()

    def carregar_resultados(self, resultados: list[dict]):
        """
        Preenche a árvore de visualização com os resultados.
        """
        self.resultados = resultados
        self.tree.clear()

        for r in resultados:
            if "erro" in r:
                continue

            tabela = r['tabela']
            colunas = r['colunas']
            linhas = r['linhas']

            item = QTreeWidgetItem([tabela])
            item.setCheckState(0, Qt.CheckState.Checked)

            registros = [
                {col: val for col, val in zip(colunas, linha)}
                for linha in linhas
            ]

            for campo in colunas:
                campo_item = QTreeWidgetItem([f" {campo}"])
                valores_unicos = []
                for reg in registros:
                    val = reg.get(campo)
                    if val is not None:
                        val_str = str(val).strip()
                        if val_str and val_str not in valores_unicos:
                            valores_unicos.append(val_str)
                    if len(valores_unicos) >= 5:
                        break
                for v in valores_unicos:
                    campo_item.addChild(QTreeWidgetItem([f"  → {v[:100]}"]))
                item.addChild(campo_item)

            self.tree.addTopLevelItem(item)

    def _exportar_csv_diagnostico(self):
        if not hasattr(self.parent_window.input_tab, "resultados_intersecao") \
        or not self.parent_window.input_tab.resultados_intersecao:
            QMessageBox.warning(self, "Aviso", "Nenhum resultado disponível para exportar.")
            return

        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar Diagnóstico CSV", "", "CSV (*.csv)")
        if not caminho:
            return

        try:
            import pandas as pd
            dados = [
                {"Tabela": r["tabela"], "Feições Encontradas": r["count"]}
                for r in self.parent_window.input_tab.resultados_intersecao
            ]
            df = pd.DataFrame(dados)
            df.to_csv(caminho, index=False, encoding="utf-8-sig")
            QMessageBox.information(self, "Sucesso", "Diagnóstico exportado com sucesso!")
            self.logger.log(f"[Export] Diagnóstico salvo em: {caminho}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar CSV:\n{e}")


    def _exportar_gpkg(self):
        if not self.resultados:
            QMessageBox.warning(self, "Aviso", "Nenhum resultado para exportar.")
            return

        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar GeoPackage", "", "GeoPackage (*.gpkg)")
        if not caminho:
            return

        try:
            # Determina as camadas marcadas pelo usuário
            selecionadas = []
            for i in range(self.tree.topLevelItemCount()):
                item = self.tree.topLevelItem(i)
                if item.checkState(0) == Qt.CheckState.Checked:
                    selecionadas.append(item.text(0))

            if not selecionadas:
                QMessageBox.warning(self, "Aviso", "Nenhuma camada selecionada.")
                return

            aoi_path = getattr(self.parent_window.input_tab, "aoi_path", None)
            if not aoi_path:
                QMessageBox.warning(self, "Erro", "AOI não disponível.")
                return

            conn = self.parent_window.input_tab.conn
            schema = self.parent_window.input_tab.schema_combo.currentText()

            exporter = GPKGExporter(conn, AOI(aoi_path).wkt, schema)
            exporter.export_layers(
                selecionadas,
                caminho,
                log_func=self.logger.log,
                aoi_path=aoi_path
            )

            QMessageBox.information(self, "Sucesso", "GeoPackage exportado com sucesso!")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar GeoPackage:\n{e}")
