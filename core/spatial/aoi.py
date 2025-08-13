"""
Este módulo define a classe AOI, que encapsula a leitura e manipulação
de uma Área de Interesse (AOI) a partir de um arquivo GeoJSON.

Ela garante que:
- A geometria seja convertida para EPSG:4674
- Uma geometria unificada em WKT esteja disponível
- A AOI possa ser exportada para GeoPackage (opcional)
"""

import geopandas as gpd


class AOI:
    def __init__(self, filepath: str):
        """
        Lê o arquivo GeoJSON e converte o sistema de referência para EPSG:4674.
        """
        self.filepath = filepath
        self.gdf = gpd.read_file(filepath).to_crs(epsg=4674)

    @property
    def wkt(self) -> str:
        """
        Retorna a geometria da AOI unificada como WKT.
        Ideal para uso em consultas ST_Intersects.
        """
        return self.gdf.geometry.union_all().wkt

    def save_to_geopackage(self, output_path: str, layer_name: str = "AOI"):
        """
        Exporta a AOI para um arquivo GeoPackage (.gpkg).
        """
        self.gdf.to_file(
            output_path,
            layer=layer_name,
            driver="GPKG",
            encoding="utf-8"
        )
