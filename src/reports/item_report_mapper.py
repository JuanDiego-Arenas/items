from typing import Any, ClassVar

from src.clients.items_client import Item, ItemCriterio, ItemDescripcionTecnica

# Ids de plan usado para ubicar criterios específicos del item.
PLAN_ID_LABORATORIO = "001"
PLAN_ID_NIVEL_RIESGO = "007"

# Nombres de campo usados para ubicar descripciones técnicas del item.
CAMPO_CODIGO_INVIMA = "CODIGO INVIMA"
CAMPO_FECHA_VCTO_INVIMA = "FECHA DE VCTO INVIMA"
CAMPO_ESTADO = "ESTADO"
CAMPO_CUM_EXPEDIENTE = "CUM/EXPEDIENTE"


class ItemReportMapper:
    HEADERS: ClassVar[list[str]] = [
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

    def map_item(
        self,
        item: Item,
    ) -> dict[str, Any]:
        # Se indexan criterios y descripciones técnicas una sola vez
        # por item, en lugar de recorrer las listas linealmente por
        # cada campo del reporte (antes hasta 6 escaneos por item).
        criterios_por_plan = self._index_criterios(item.criterios)

        tecnicas_por_campo = self._index_descripciones_tecnicas(
            item.descripciones_tecnicas,
        )

        return {
            "CODIGOS DE BARRAS": self._value(
                item.codigo_barra_principal,
            ),
            "REFERENCIAALTERNA": self._value(
                item.referencia_alterna,
            ),
            "ITEM": self._value(
                item.item,
            ),
            "DESCRIP. ITEM": self._value(
                item.descripcion_item,
            ),
            "U.M.": self._value(
                item.unidad_inventario,
            ),
            "LAB Descripcion corta)": self._value(
                item.descripcion_corta_item,
            ),
            "LABORATORIO/MARCA": self._criterio_descripcion(
                criterios_por_plan,
                plan_id=PLAN_ID_LABORATORIO,
            ),
            "NIVEL DE RIESGO": self._nivel_riesgo(
                criterios_por_plan,
            ),
            "INVIMA": self._tecnica_valor(
                tecnicas_por_campo,
                campo=CAMPO_CODIGO_INVIMA,
            ),
            "FECHA VTO INVIMA": self._tecnica_valor(
                tecnicas_por_campo,
                campo=CAMPO_FECHA_VCTO_INVIMA,
            ),
            "ESTADO DEL REGISTO": self._tecnica_valor(
                tecnicas_por_campo,
                campo=CAMPO_ESTADO,
            ),
            "CODIGO UNSPSC": self._value(
                item.id_codigo_unspsc,
            ),
            "DESC.CODIGOS UNSPSC": self._value(
                item.descripcion_codigo_unspsc,
            ),
            "CUM/EXISTENCIA": self._tecnica_valor(
                tecnicas_por_campo,
                campo=CAMPO_CUM_EXPEDIENTE,
            ),
        }

    def map_items(
        self,
        items: list[Item],
    ) -> list[dict[str, Any]]:
        return [self.map_item(item) for item in items]

    @staticmethod
    def _value(
        value: Any,
    ) -> Any:
        if value is None:
            return ""

        return value

    @staticmethod
    def _index_criterios(
        criterios: list[ItemCriterio],
    ) -> dict[str, ItemCriterio]:
        """Indexa los criterios por id_plan (normalizado con strip)."""
        index: dict[str, ItemCriterio] = {}

        for criterio in criterios:
            if not criterio.id_plan:
                continue

            plan_id = criterio.id_plan.strip()

            if plan_id and plan_id not in index:
                index[plan_id] = criterio

        return index

    @staticmethod
    def _index_descripciones_tecnicas(
        descripciones: list[ItemDescripcionTecnica],
    ) -> dict[str, ItemDescripcionTecnica]:
        """Indexa las descripciones técnicas por campo
        (normalizado con strip + upper).
        """
        index: dict[str, ItemDescripcionTecnica] = {}

        for descripcion in descripciones:
            if not descripcion.campo:
                continue

            campo = descripcion.campo.strip().upper()

            if campo and campo not in index:
                index[campo] = descripcion

        return index

    @staticmethod
    def _criterio_descripcion(
        criterios_por_plan: dict[str, ItemCriterio],
        plan_id: str,
    ) -> str:
        criterio = criterios_por_plan.get(plan_id)

        if criterio is None:
            return ""

        return ItemReportMapper._value(
            criterio.descripcion_criterio,
        )

    @staticmethod
    def _nivel_riesgo(
        criterios_por_plan: dict[str, ItemCriterio],
    ) -> str:
        criterio = criterios_por_plan.get(PLAN_ID_NIVEL_RIESGO)

        if criterio is None:
            return ""

        id_criterio = criterio.id_criterio.strip() if criterio.id_criterio else ""

        descripcion = (
            criterio.descripcion_criterio.strip()
            if criterio.descripcion_criterio
            else ""
        )

        if id_criterio and descripcion:
            return f"{id_criterio} - {descripcion}"

        return id_criterio or descripcion

    @staticmethod
    def _tecnica_valor(
        tecnicas_por_campo: dict[str, ItemDescripcionTecnica],
        campo: str,
    ) -> str:
        descripcion = tecnicas_por_campo.get(campo.upper())

        if descripcion is None:
            return ""

        return ItemReportMapper._value(
            descripcion.valor,
        )
