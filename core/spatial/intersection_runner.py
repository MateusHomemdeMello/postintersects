"""
Este módulo define a classe IntersectionRunner, que executa interseções espaciais
entre uma Área de Interesse (AOI) e tabelas espaciais de um esquema no banco PostGIS.

Cada tabela é verificada com a função ST_Intersects e o número de feições resultantes
é contabilizado.

Resultado: uma lista de dicionários contendo o nome da tabela, a contagem de interseções,
as colunas não-geométricas e algumas linhas amostrais.
"""

from psycopg2.extensions import connection


class IntersectionRunner:
    def __init__(self, conn: connection, aoi_wkt: str, schema: str, tables: list[str]):
        self.conn = conn
        self.aoi_wkt = aoi_wkt
        self.schema = schema
        self.tables = tables

    def run(self, conn, schema, aoi_geojson, include_zero=False, output_csv=None):
        """
        Executa a interseção espacial entre a AOI e todas as tabelas do esquema.
        Também gera um diagnóstico com a contagem de feições por camada.
        """
        import geopandas as gpd
        from shapely.geometry import shape
        import csv

        self.diagnostico = []

        try:
            with conn.cursor() as cur:
                # Lista todas as tabelas com coluna de geometria
                cur.execute(f"""
                    SELECT table_name, column_name
                    FROM information_schema.columns
                    WHERE table_schema = %s
                    AND udt_name = 'geometry'
                """, (schema,))
                tabelas = cur.fetchall()

            # Converte AOI para Shapely
            aoi_geom = shape(aoi_geojson["features"][0]["geometry"])

            resultados = {}

            for tabela, geom_col in tabelas:
                try:
                    query = f"""
                        SELECT * FROM {schema}."{tabela}"
                        WHERE ST_Intersects(
                            {geom_col},
                            ST_GeomFromText(%s, 4674)
                        )
                    """
                    with conn.cursor() as cur:
                        cur.execute(query, (aoi_geom.wkt,))
                        rows = cur.fetchall()

                    count = len(rows)
                    if include_zero or count > 0:
                        resultados[tabela] = rows

                    # Adiciona ao diagnóstico
                    self.diagnostico.append({"Tabela": tabela, "Feições Encontradas": count})

                except Exception as e:
                    self.logger.error(f"[Interseção] Erro na camada {tabela}: {e}")
                    self.diagnostico.append({"Tabela": tabela, "Feições Encontradas": 0})

            # Log detalhado igual ao script original
            self.logger.info("[Diagnóstico por camada]")
            for item in self.diagnostico:
                self.logger.info(f"{item['Tabela']} -> {item['Feições Encontradas']}")

            # Salva CSV do diagnóstico, se solicitado
            if output_csv:
                with open(output_csv, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["Tabela", "Feições Encontradas"])
                    writer.writeheader()
                    writer.writerows(self.diagnostico)
                self.logger.info(f"[Diagnóstico] CSV salvo em {output_csv}")

            # Log resumo
            total_intersect = sum(1 for item in self.diagnostico if item["Feições Encontradas"] > 0)
            self.logger.info(f"[Interseção] {total_intersect} camadas com interseção encontrada.")

            return resultados

        except Exception as e:
            self.logger.error(f"[Interseção] Erro ao executar interseções: {e}")
            return {}


    def diagnostico_counts(self, include_zero=True) -> list[dict]:
        """
        Gera a lista 'Tabela' -> 'Feições Encontradas' para TODAS as tabelas consultadas.
        Retorna exatamente o que queremos ver no log e exportar em CSV.
        """
        resultados = []
        for tabela in self.tabelas:  # use 'self.tables' se esse for o nome no seu __init__
            try:
                query = f"""
                    SELECT COUNT(*)
                    FROM "{self.schema}"."{tabela}"
                    WHERE geom IS NOT NULL
                    AND ST_IsValid(geom)
                    AND ST_SRID(geom) = 4674
                    AND ST_Intersects(geom, ST_GeomFromText(%s, 4674));
                """
                with self.conn.cursor() as cur:
                    cur.execute(query, (self.aoi_wkt,))
                    count = cur.fetchone()[0]
                if include_zero or count > 0:
                    resultados.append({"Tabela": tabela, "Feições Encontradas": count})
            except Exception as e:
                # Se der erro na camada, registramos 0 e o erro (opcional)
                resultados.append({"Tabela": tabela, "Feições Encontradas": 0, "erro": str(e)})
        return resultados
