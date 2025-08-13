import psycopg2
from psycopg2.extensions import connection as _connection


class PostgresConnector:
    def __init__(self, config: dict):
        """
        Inicializa o conector com as credenciais necessárias.
        Espera um dicionário com as chaves:
        host, port, dbname, user, password
        """
        self.config = config
        self.conn: _connection | None = None

    def connect(self) -> _connection:
        """
        Estabelece a conexão com o banco de dados.
        Retorna a conexão se bem-sucedida ou levanta um erro.
        """
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(**self.config)
        return self.conn

    def is_connected(self) -> bool:
        """
        Retorna True se a conexão está ativa.
        """
        return self.conn is not None and self.conn.closed == 0

    def close(self):
        """
        Encerra a conexão com o banco, se estiver ativa.
        """
        if self.conn and self.conn.closed == 0:
            self.conn.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
