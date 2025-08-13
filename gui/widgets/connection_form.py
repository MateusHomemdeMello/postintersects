"""
Este módulo define o widget ConnectionForm, um componente reutilizável da interface
que permite entrada e recuperação de credenciais de conexão com um banco PostgreSQL.

Campos incluídos:
- Host
- Porta
- Banco
- Usuário
- Senha
"""

from PyQt6.QtWidgets import QLineEdit, QHBoxLayout, QWidget


class ConnectionForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.host_input = QLineEdit(); self.host_input.setPlaceholderText("Host")
        self.port_input = QLineEdit(); self.port_input.setPlaceholderText("Porta"); self.port_input.setText("5432")
        self.db_input = QLineEdit(); self.db_input.setPlaceholderText("Banco")
        self.user_input = QLineEdit(); self.user_input.setPlaceholderText("Usuário")
        self.pass_input = QLineEdit(); self.pass_input.setPlaceholderText("Senha"); self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        for field in [self.host_input, self.port_input, self.db_input, self.user_input, self.pass_input]:
            field.setMaximumWidth(120)
            layout.addWidget(field)

        self.setLayout(layout)

    def get_data(self) -> dict:
        """
        Retorna os dados preenchidos como um dicionário.
        """
        return {
            "host": self.host_input.text(),
            "port": self.port_input.text(),
            "dbname": self.db_input.text(),
            "user": self.user_input.text(),
            "password": self.pass_input.text()
        }

    def set_data(self, data: dict):
        """
        Preenche os campos a partir de um dicionário.
        """
        self.host_input.setText(data.get("host", ""))
        self.port_input.setText(str(data.get("port", "")))
        self.db_input.setText(data.get("dbname", ""))
        self.user_input.setText(data.get("user", ""))
        self.pass_input.setText(data.get("password", ""))

    def clear(self):
        """
        Limpa todos os campos do formulário.
        """
        for field in [self.host_input, self.port_input, self.db_input, self.user_input, self.pass_input]:
            field.clear()
