from src.clients.items_client import (
    Item,
    ItemCriterio,
    ItemDescripcionTecnica,
)
from src.reports.item_report_mapper import ItemReportMapper


def build_item(**overrides) -> Item:
    """Crea un Item de prueba con valores por defecto sensatos,
    permitiendo sobreescribir cualquier campo puntual.
    """
    defaults = {
        "idCompania": 1,
        "item": 100,
        "descripcionItem": "Item de prueba",
        "descripcionCortaItem": "Corta",
        "referenciaAlterna": "REF-1",
        "codigoBarraPrincipal": "7701234567890",
        "unidadInventario": "CAJA",
        "idCodigoUnspsc": "51102706",
        "descripcionCodigoUnspsc": "Analgésicos",
        "criterios": [],
        "descripcionesTecnicas": [],
    }

    defaults.update(overrides)

    return Item.model_validate(defaults)


class TestMapItemCamposBasicos:
    def test_mapea_campos_directos_del_item(self):
        item = build_item()
        mapper = ItemReportMapper()

        row = mapper.map_item(item)

        assert row["CODIGOS DE BARRAS"] == "7701234567890"
        assert row["REFERENCIAALTERNA"] == "REF-1"
        assert row["ITEM"] == 100
        assert row["DESCRIP. ITEM"] == "Item de prueba"
        assert row["U.M."] == "CAJA"
        assert row["LAB Descripcion corta)"] == "Corta"
        assert row["CODIGO UNSPSC"] == "51102706"
        assert row["DESC.CODIGOS UNSPSC"] == "Analgésicos"

    def test_valores_none_se_mapean_a_cadena_vacia(self):
        item = build_item(
            codigoBarraPrincipal=None,
            referenciaAlterna=None,
        )
        mapper = ItemReportMapper()

        row = mapper.map_item(item)

        assert row["CODIGOS DE BARRAS"] == ""
        assert row["REFERENCIAALTERNA"] == ""

    def test_headers_definen_el_orden_y_las_columnas_del_reporte(self):
        assert ItemReportMapper.HEADERS == [
            "CODIGOS DE BARRAS",
            "REFERENCIAALTERNA",
            "ITEM",
            "DESCRIP. ITEM",
            "U.M.",
            "LAB Descripcion corta)",
            "LABORATORIO/MARCA",
            "NIVEL DE RIESGO",
            "INVIMA",
            "FECHA VTO INVIMA",
            "ESTADO DEL REGISTO",
            "CODIGO UNSPSC",
            "DESC.CODIGOS UNSPSC",
            "CUM/EXISTENCIA",
        ]


class TestCriterios:
    def test_obtiene_laboratorio_desde_criterio_plan_001(self):
        item = build_item(
            criterios=[
                ItemCriterio(
                    idPlan="001",
                    descripcionPlan="Laboratorio",
                    idCriterio="LAB-1",
                    descripcionCriterio="Laboratorios ACME",
                ),
            ],
        )
        mapper = ItemReportMapper()

        row = mapper.map_item(item)

        assert row["LABORATORIO/MARCA"] == "Laboratorios ACME"

    def test_criterio_con_id_plan_con_espacios_se_normaliza(self):
        item = build_item(
            criterios=[
                ItemCriterio(
                    idPlan=" 001 ",
                    descripcionCriterio="Laboratorios ACME",
                ),
            ],
        )
        mapper = ItemReportMapper()

        row = mapper.map_item(item)

        assert row["LABORATORIO/MARCA"] == "Laboratorios ACME"

    def test_laboratorio_vacio_si_no_hay_criterio_plan_001(self):
        item = build_item(
            criterios=[
                ItemCriterio(idPlan="002", descripcionCriterio="Otro"),
            ],
        )
        mapper = ItemReportMapper()

        row = mapper.map_item(item)

        assert row["LABORATORIO/MARCA"] == ""

    def test_nivel_de_riesgo_combina_id_y_descripcion(self):
        item = build_item(
            criterios=[
                ItemCriterio(
                    idPlan="007",
                    idCriterio="III",
                    descripcionCriterio="Riesgo alto",
                ),
            ],
        )
        mapper = ItemReportMapper()

        row = mapper.map_item(item)

        assert row["NIVEL DE RIESGO"] == "III - Riesgo alto"

    def test_nivel_de_riesgo_solo_con_id_criterio(self):
        item = build_item(
            criterios=[
                ItemCriterio(idPlan="007", idCriterio="III"),
            ],
        )
        mapper = ItemReportMapper()

        row = mapper.map_item(item)

        assert row["NIVEL DE RIESGO"] == "III"

    def test_nivel_de_riesgo_solo_con_descripcion(self):
        item = build_item(
            criterios=[
                ItemCriterio(idPlan="007", descripcionCriterio="Riesgo alto"),
            ],
        )
        mapper = ItemReportMapper()

        row = mapper.map_item(item)

        assert row["NIVEL DE RIESGO"] == "Riesgo alto"

    def test_criterio_sin_id_plan_se_ignora(self):
        item = build_item(
            criterios=[
                ItemCriterio(idPlan=None, descripcionCriterio="Ignorado"),
            ],
        )
        mapper = ItemReportMapper()

        row = mapper.map_item(item)

        assert row["LABORATORIO/MARCA"] == ""
        assert row["NIVEL DE RIESGO"] == ""

    def test_con_criterios_duplicados_para_el_mismo_plan_conserva_el_primero(self):
        item = build_item(
            criterios=[
                ItemCriterio(idPlan="001", descripcionCriterio="Primero"),
                ItemCriterio(idPlan="001", descripcionCriterio="Segundo"),
            ],
        )
        mapper = ItemReportMapper()

        row = mapper.map_item(item)

        assert row["LABORATORIO/MARCA"] == "Primero"


class TestDescripcionesTecnicas:
    def test_obtiene_invima_fecha_y_estado_por_campo(self):
        item = build_item(
            descripcionesTecnicas=[
                ItemDescripcionTecnica(
                    campo="CODIGO INVIMA",
                    valor="INV-123",
                ),
                ItemDescripcionTecnica(
                    campo="FECHA DE VCTO INVIMA",
                    valor="2030-01-01",
                ),
                ItemDescripcionTecnica(
                    campo="ESTADO",
                    valor="Vigente",
                ),
                ItemDescripcionTecnica(
                    campo="CUM/EXPEDIENTE",
                    valor="CUM-999",
                ),
            ],
        )
        mapper = ItemReportMapper()

        row = mapper.map_item(item)

        assert row["INVIMA"] == "INV-123"
        assert row["FECHA VTO INVIMA"] == "2030-01-01"
        assert row["ESTADO DEL REGISTO"] == "Vigente"
        assert row["CUM/EXISTENCIA"] == "CUM-999"

    def test_busqueda_de_campo_es_insensible_a_mayusculas_y_espacios(self):
        item = build_item(
            descripcionesTecnicas=[
                ItemDescripcionTecnica(
                    campo=" codigo invima ",
                    valor="INV-123",
                ),
            ],
        )
        mapper = ItemReportMapper()

        row = mapper.map_item(item)

        assert row["INVIMA"] == "INV-123"

    def test_campo_faltante_se_mapea_a_cadena_vacia(self):
        item = build_item(descripcionesTecnicas=[])
        mapper = ItemReportMapper()

        row = mapper.map_item(item)

        assert row["INVIMA"] == ""
        assert row["FECHA VTO INVIMA"] == ""
        assert row["ESTADO DEL REGISTO"] == ""
        assert row["CUM/EXISTENCIA"] == ""

    def test_descripcion_tecnica_sin_campo_se_ignora(self):
        item = build_item(
            descripcionesTecnicas=[
                ItemDescripcionTecnica(campo=None, valor="Ignorado"),
            ],
        )
        mapper = ItemReportMapper()

        row = mapper.map_item(item)

        assert row["INVIMA"] == ""

    def test_con_campos_duplicados_conserva_el_primero(self):
        item = build_item(
            descripcionesTecnicas=[
                ItemDescripcionTecnica(campo="ESTADO", valor="Primero"),
                ItemDescripcionTecnica(campo="ESTADO", valor="Segundo"),
            ],
        )
        mapper = ItemReportMapper()

        row = mapper.map_item(item)

        assert row["ESTADO DEL REGISTO"] == "Primero"


class TestMapItems:
    def test_mapea_una_lista_de_items_preservando_el_orden(self):
        items = [
            build_item(item=1, descripcionItem="Uno"),
            build_item(item=2, descripcionItem="Dos"),
        ]
        mapper = ItemReportMapper()

        rows = mapper.map_items(items)

        assert [row["ITEM"] for row in rows] == [1, 2]
        assert [row["DESCRIP. ITEM"] for row in rows] == ["Uno", "Dos"]

    def test_lista_vacia_produce_lista_vacia(self):
        mapper = ItemReportMapper()

        assert mapper.map_items([]) == []
