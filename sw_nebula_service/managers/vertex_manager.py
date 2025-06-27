from typing import Any

from pydantic import BaseModel
from rich import print as rprint
from sw_onto_generation.base.base_node import BaseNode

from sw_nebula_service.managers.connector import Connector
from sw_nebula_service.managers.utils import convert_node_to_nebula_data, format_field_value, pascal_case_to_snake_case
from sw_nebula_service.models.nodes import BaseNebulaNode


class VertexManager:
    def __init__(self, connector: Connector):
        self.connector = connector

    def insert_vertex(self, name_space: str, node: BaseNode | BaseNebulaNode | BaseModel, vid: str) -> None:
        tag_name, field_names_str, values_str = convert_node_to_nebula_data(node)
        query = f'INSERT VERTEX IF NOT EXISTS {tag_name} ({field_names_str}) VALUES "{vid}": ({values_str})'  # noqa: S608
        rprint(f"query: {query}")
        with self.connector.session(name_space) as session:
            result = session.execute(query)
            if result.is_succeeded():
                rprint(f"Node {vid} inserted successfully")
            else:
                raise Exception(f"Failed to insert node instance for tag {tag_name}: {result.error_msg()}")

    def get_vertex(self, name_space: str, node_class: type[BaseNode] | type[BaseNebulaNode]) -> list[BaseNode | BaseNebulaNode]:
        tag_name = pascal_case_to_snake_case(node_class.__name__)
        query = f"MATCH (n:{tag_name}) RETURN n"
        nodes = []
        with self.connector.session(name_space) as session:
            result = session.execute(query)
            if result.is_succeeded():
                for res in result.as_primitive():
                    data = res["n"]["tags"]
                    node = node_class(**data[tag_name])
                    nodes.append(node)
            else:
                raise Exception(f"Failed to get vertex for tag {tag_name}: {result.error_msg()}")
        return nodes

    def update_vertex_field(self, name_space: str, tag_name: str, vid: str, field_name: str, value: Any) -> None:
        nebula_value = format_field_value(value)
        with self.connector.session(name_space) as session:
            query = f'UPDATE VERTEX ON {tag_name} "{vid}" SET {field_name} = {nebula_value}'  # noqa: S608
            result = session.execute(query)
            rprint(f"query: {query}")
            if result.is_succeeded():
                rprint(f"Node {vid} updated successfully")
            else:
                raise Exception(f"Failed to update node field value for tag {tag_name}: {result.error_msg()}")
