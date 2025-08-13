from psycopg2.extensions import connection


class SchemaManager:
    def __init__(self, conn: connection):
        """
        Recebe uma conexão ativa com o banco PostgreSQL.
        """
        self.conn = conn

    def list_schemas(self) -> list[str]:
        """
        Lista os esquemas do banco, ignorando os internos.
        """
        query = "SELECT schema_name FROM information_schema.schemata;"
        ignorar = {"pg_catalog", "information_schema"}

        with self.conn.cursor() as cur:
            cur.execute(query)
            resultados = [row[0] for row in cur.fetchall()]
            return sorted([s for s in resultados if s not in ignorar])

    def list_geometry_tables(self, schema: str) -> list[str]:
        """
        Lista os nomes das tabelas espaciais (com colunas geométricas)
        dentro de um esquema fornecido.
        """
        query = """
            SELECT f_table_name 
            FROM geometry_columns 
            WHERE f_table_schema = %s;
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (schema,))
            return [row[0] for row in cur.fetchall()]
