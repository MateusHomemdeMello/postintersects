"""
Este módulo define a classe GPKGExporter, que exporta múltiplas tabelas espaciais
para um único arquivo GeoPackage (.gpkg), filtrando apenas as feições que intersectam
uma Área de Interesse (AOI) definida por WKT.

Inclui:
- Validação das geometrias
- Conversão de geometrias ZM para Z
"""

import geopandas as gpd
from shapely.geometry import mapping, shape
from psycopg2.extensions import connection
from core.spatial.aoi import AOI


class GPKGExporter:
    def __init__(self, conn: connection, aoi_wkt: str, schema: str):
        self.conn = conn
        self.aoi_wkt = aoi_wkt
        self.schema = schema

    def export_layers(self, layer_names: list[str], output_path: str, log_func=print, aoi_path: str = None):
        """
        Exporta as camadas selecionadas para um GeoPackage.

        Parâmetros:
        - layer_names: lista com os nomes das tabelas selecionadas
        - output_path: caminho final do arquivo .gpkg
        - log_func: função opcional de log (ex: self.log_box.append)
            """

        # Se tiver caminho da AOI, adiciona como primeira camada
        if aoi_path:
            try:
                aoi_gdf = gpd.read_file(aoi_path).to_crs(epsg=4674)
                aoi_gdf.to_file(output_path, layer="AOI", driver="GPKG")
                log_func("[OK] Camada 'AOI' exportada para o GeoPackage.")
            except Exception as e:
                log_func(f"[Erro] Falha ao exportar camada 'AOI': {e}")
                                
                
        for tabela in layer_names:
            try:
                query = f'''
                    SELECT * FROM "{self.schema}"."{tabela}"
                    WHERE ST_Intersects(geom, ST_GeomFromText(%s, 4674))
                '''
                gdf = gpd.read_postgis(query, self.conn, geom_col="geom", params=[self.aoi_wkt])

                if gdf.empty:
                    log_func(f"[Aviso] Tabela '{tabela}' não possui feições para exportar.")
                    continue

                gdf = gdf[gdf.is_valid & ~gdf.is_empty]
                if gdf.empty:
                    log_func(f"[Aviso] Tabela '{tabela}' só possui geometrias inválidas ou vazias.")
                    continue

                if any("ZM" in str(geom) for geom in gdf.geometry):
                    log_func(f"[Aviso] Geometrias ZM convertidas para Z na camada '{tabela}'.")
                    gdf["geometry"] = gdf["geometry"].apply(self._remove_m)

                gdf.to_file(
                    output_path,
                    layer=tabela,
                    driver="GPKG",
                    encoding="utf-8",
                    geometry_type=None
                )

                log_func(f"[OK] Camada '{tabela}' exportada para GeoPackage.")

            except Exception as e:
                log_func(f"[Erro] Falha ao exportar '{tabela}': {e}")

    def _remove_m(self, geom):
        """
        Remove a componente M das geometrias do tipo ZM.
        """
        geom_dict = mapping(geom)
        if "coordinates" in geom_dict:
            def strip_m(coords):
                if isinstance(coords[0], (float, int)):
                    return coords[:3]  # ponto
                return [strip_m(c) for c in coords]
            geom_dict["coordinates"] = strip_m(geom_dict["coordinates"])
        return shape(geom_dict)
