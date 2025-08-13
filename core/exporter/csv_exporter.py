# diglet/core/exporter/csv_exporter.py

"""
Este módulo define a classe CSVExporter, que exporta um resumo do diagnóstico
espacial para um arquivo CSV. Cada linha contém:

- O nome da tabela espacial
- A quantidade de feições que intersectaram a AOI

Ideal para relatórios rápidos ou integração com outras ferramentas.
"""

import pandas as pd


class CSVExporter:
    @staticmethod
    def export(resultados: list[dict], output_path: str):
        """
        Exporta os resultados de interseção para um arquivo CSV.

        Parâmetros:
        - resultados: lista de dicionários contendo 'tabela' e 'count'
        - output_path: caminho completo para salvar o arquivo .csv
        """
        dados = [
            {"Tabela": r["tabela"], "Feições Encontradas": r["count"]}
            for r in resultados
            if "count" in r  # ignora entradas com erro
        ]
        df = pd.DataFrame(dados)
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
