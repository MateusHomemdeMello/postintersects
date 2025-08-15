"""
Este módulo define a classe InputTab, responsável por montar a interface da aba
de entrada da aplicação. Esta aba inclui:

- Formulário de conexão com o banco PostgreSQL/PostGIS
- Importação/exportação de credenciais via JSON
- Seleção de esquema, arquivo GeoJSON (AOI), e botões de execução
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QComboBox,
    QPushButton, QFileDialog, QMessageBox, QFrame, QTextEdit
)
from PyQt6.QtCore import Qt
from core.db.connector import PostgresConnector
from core.db.schema_manager import SchemaManager
from core.spatial.aoi import AOI
from core.spatial.intersection_runner import IntersectionRunner
from core.exporter.csv_exporter import CSVExporter
from utils.logger import Logger
import json
import os


class InputTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # referência à MainWindow

        self.conn = None
        self.aoi_path = None
        self.resultados = []
        self.tabelas_com_geometria = []

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Título principal
        titulo = QLabel("PostIntersect")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size: 24pt; font-weight: bold; color: #3daee9; margin-top: 12px;")
        layout.addWidget(titulo)

        subtitulo = QLabel("Consultas de Interseção Espacial no PostGIS")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setStyleSheet("font-size: 10.5pt; margin-bottom: 12px;")
        layout.addWidget(subtitulo)

        # Linha de entrada de conexão
        self._add_conexao_form(layout)

        # Linha separadora
        layout.addWidget(self._linha())

        # ComboBox de esquemas
        schema_row = QHBoxLayout()
        self.schema_combo = QComboBox()
        self.schema_combo.setEnabled(False)
        schema_row.addWidget(QLabel("Esquema:"))
        schema_row.addWidget(self.schema_combo)
        layout.addLayout(schema_row)

        # Seletor de GeoJSON
        geo_row = QHBoxLayout()
        self.geojson_input = QLineEdit(); self.geojson_input.setReadOnly(True)
        self.geojson_btn = QPushButton("Selecionar AOI")
        self.geojson_btn.clicked.connect(self._selecionar_geojson)
        geo_row.addWidget(QLabel("AOI (GeoJSON):"))
        geo_row.addWidget(self.geojson_input)
        geo_row.addWidget(self.geojson_btn)
        layout.addLayout(geo_row)

        # Botões principais
        btn_row = QHBoxLayout()
        self.buscar_btn = QPushButton("Buscar Tabelas")
        self.buscar_btn.setEnabled(False)
        self.buscar_btn.clicked.connect(self._buscar_tabelas)

        self.executar_btn = QPushButton("Executar Interseção")
        self.executar_btn.setEnabled(False)
        self.executar_btn.clicked.connect(self._executar_intersecoes)

        btn_row.addWidget(self.buscar_btn)
        btn_row.addWidget(self.executar_btn)
        layout.addLayout(btn_row)

        # Log visual
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMinimumHeight(110)
        self.log_box.setStyleSheet("font-family: 'Consolas'; font-size: 10pt;")
        layout.addWidget(self.log_box)

        self.logger = Logger(self.log_box)

        layout.addStretch()

    def _add_conexao_form(self, layout):
        """
        Cria os campos de conexão e os botões de importar/exportar JSON.
        """
        row = QHBoxLayout()
        self.host_input = QLineEdit(); self.host_input.setPlaceholderText("Host")
        self.port_input = QLineEdit(); self.port_input.setPlaceholderText("Porta"); self.port_input.setText("5432")
        self.db_input = QLineEdit(); self.db_input.setPlaceholderText("Banco")
        self.user_input = QLineEdit(); self.user_input.setPlaceholderText("Usuário")
        self.pass_input = QLineEdit(); self.pass_input.setPlaceholderText("Senha"); self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        for widget in [self.host_input, self.port_input, self.db_input, self.user_input, self.pass_input]:
            widget.setMaximumWidth(120)
            row.addWidget(widget)

        layout.addLayout(row)

        btns = QHBoxLayout()
        self.importar_btn = QPushButton("Importar Credenciais")
        self.importar_btn.clicked.connect(self._importar_credenciais)

        self.exportar_btn = QPushButton("Exportar Credenciais")
        self.exportar_btn.clicked.connect(self._exportar_credenciais)

        self.conectar_btn = QPushButton("Conectar")
        self.conectar_btn.clicked.connect(self._conectar)

        btns.addWidget(self.importar_btn)
        btns.addWidget(self.exportar_btn)
        btns.addWidget(self.conectar_btn)
        layout.addLayout(btns)

    def _linha(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #444; margin: 8px 0;")
        return line


    def _importar_credenciais(self):
        """
        Lê um arquivo JSON contendo credenciais e preenche o formulário.
        """
        caminho, _ = QFileDialog.getOpenFileName(self, "Selecionar arquivo JSON", "", "JSON (*.json)")
        if not caminho:
            return

        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)

            for campo in ["host", "port", "dbname", "user", "password"]:
                if campo not in dados:
                    raise ValueError(f"Campo ausente: {campo}")

            self.host_input.setText(dados["host"])
            self.port_input.setText(str(dados["port"]))
            self.db_input.setText(dados["dbname"])
            self.user_input.setText(dados["user"])
            self.pass_input.setText(dados["password"])

            self.logger.log(f"[Import] Credenciais carregadas de: {os.path.basename(caminho)}")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao importar JSON:\n{e}")
            self.logger.log(f"[Erro] Falha ao importar credenciais: {e}")

    def _exportar_credenciais(self):
        """
        Salva os campos de conexão como arquivo JSON.
        """
        dados = {
            "host": self.host_input.text(),
            "port": self.port_input.text(),
            "dbname": self.db_input.text(),
            "user": self.user_input.text(),
            "password": self.pass_input.text()
        }

        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar JSON", "", "JSON (*.json)")
        if not caminho:
            return

        try:
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            self.logger.log(f"[Export] Credenciais salvas em: {caminho}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar JSON:\n{e}")
            self.logger.log(f"[Erro] Falha ao exportar credenciais: {e}")

    def _conectar(self):
        """
        Estabelece conexão com o banco e carrega os esquemas disponíveis.
        """
        config = {
            "host": self.host_input.text(),
            "port": self.port_input.text(),
            "dbname": self.db_input.text(),
            "user": self.user_input.text(),
            "password": self.pass_input.text()
        }

        try:
            self.conn = PostgresConnector(config).connect()
            manager = SchemaManager(self.conn)
            esquemas = manager.list_schemas()
            self.schema_combo.clear()
            self.schema_combo.addItems(esquemas)
            self.schema_combo.setEnabled(True)
            self.buscar_btn.setEnabled(True)

            self.logger.log("[Conexão] Banco conectado com sucesso.")
            self.logger.log(f"[Esquemas] Disponíveis: {esquemas}")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao conectar:\n{e}")
            self.logger.log(f"[Erro] Falha na conexão: {e}")

    def _selecionar_geojson(self):
        """
        Seleciona o arquivo GeoJSON da AOI e armazena o caminho.
        """
        caminho, _ = QFileDialog.getOpenFileName(self, "Selecionar GeoJSON", "", "GeoJSON (*.geojson)")
        if caminho:
            self.aoi_path = caminho
            self.geojson_input.setText(caminho)
            self.logger.log(f"[AOI] Selecionado: {os.path.basename(caminho)}")

    def _buscar_tabelas(self):
        """
        Lista as tabelas espaciais do esquema selecionado.
        """
        esquema = self.schema_combo.currentText()
        try:
            manager = SchemaManager(self.conn)
            self.tabelas_com_geometria = manager.list_geometry_tables(esquema)
            self.executar_btn.setEnabled(bool(self.tabelas_com_geometria))
            self.logger.log(f"[Tabelas] Encontradas no esquema '{esquema}': {self.tabelas_com_geometria}")
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao buscar tabelas:\n{e}")
            self.logger.log(f"[Erro] Falha ao buscar tabelas: {e}")

    def _executar_intersecoes(self):
        """
        Executa ST_Intersects entre a AOI e todas as tabelas com geometria.
        """
        if not self.aoi_path:
            QMessageBox.warning(self, "Erro", "Selecione uma AOI antes de executar.")
            return

        try:
            from core.spatial.aoi import AOI
            aoi = AOI(self.aoi_path)
            esquema = self.schema_combo.currentText()

            resultados_filtrados = []   # Para ResultsTab
            resultados_diagnostico = [] # Para CSV e log

            with self.conn.cursor() as cur:
                for tabela in self.tabelas_com_geometria:
                    try:
                        # Conta feições
                        cur.execute(f"""
                            SELECT COUNT(*) 
                            FROM "{esquema}"."{tabela}"
                            WHERE geom IS NOT NULL
                            AND ST_IsValid(geom)
                            AND ST_SRID(geom) = 4674
                            AND ST_Intersects(geom, ST_GeomFromText(%s, 4674));
                        """, (aoi.wkt,))
                        count = cur.fetchone()[0]

                        # Salva no diagnóstico (todas as tabelas)
                        resultados_diagnostico.append({"tabela": tabela, "count": count})

                        # Loga no painel
                        if count > 0:
                            self.logger.log(f"[OK] {tabela} -> {count} feições intersectam")

                            # Busca dados de exemplo para ResultsTab
                            cur.execute(f"""SELECT * FROM "{esquema}"."{tabela}" LIMIT 5""")
                            colunas = [desc[0] for desc in cur.description if desc[0] != "geom"]
                            linhas = cur.fetchall()

                            resultados_filtrados.append({
                                "tabela": tabela,
                                "count": count,
                                "colunas": colunas,
                                "linhas": linhas
                            })
                        else:
                            self.logger.log(f"[Info] {tabela} -> 0 feições intersectam")

                    except Exception as e:
                        self.logger.log(f"[Erro] Falha ao processar '{tabela}': {e}")
                        resultados_diagnostico.append({"tabela": tabela, "count": 0})

            # Guarda listas para exportação
            self.resultados_intersecao = resultados_diagnostico  # Para CSV
            self.parent_window.results_tab.carregar_resultados(resultados_filtrados)  # Para interface
            self.parent_window.mostrar_aba_resultados()

            # Síntese
            total_com_intersecao = sum(1 for r in resultados_diagnostico if r["count"] > 0)
            self.logger.log(f"[Interseção] {total_com_intersecao} camadas com interseção encontrada.")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao executar interseções:\n{e}")
            self.logger.log(f"[Erro] Falha na interseção: {e}")
