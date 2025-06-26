from datetime import datetime
from typing import Any

from pydantic import BaseModel
from rich import print as rprint
from sw_onto_generation.base.base_node import BaseNode

from sw_nebula_service.managers.connector import Connector
from sw_nebula_service.models.nodes import BaseNebulaNode
from sw_nebula_service.utils import pascal_case_to_snake_case


def format_field_value(value: Any) -> str:
    if isinstance(value, datetime):
        return f'datetime("{value.strftime("%Y-%m-%dT%H:%M:%S")}")'
    elif isinstance(value, float):
        return str(value)
    elif value is None:
        return "NULL"
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, str):
        return f'"{str(value)}"'
    else:
        raise ValueError(f"value: {value} is not supported")


def find_class_by_tag_name(tag_name: str) -> type[BaseNode] | type[BaseNebulaNode] | type[BaseModel]:
    pass


def convert_node_to_nebula_data(node: BaseNode | BaseNebulaNode | BaseModel) -> dict[str, Any]:
    data = node.model_dump()
    tag_name = pascal_case_to_snake_case(node.__class__.__name__)
    formatted_data = []
    field_names = []
    for field_name in list(data.keys()):
        field_names.append(field_name)
        value = data.get(field_name)
        formatted_data.append(format_field_value(value))
    field_names_str = ", ".join(field_names)
    values_str = ", ".join(formatted_data)
    return tag_name, field_names_str, values_str


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

    def get_vertex(self, name_space: str, tag_name: str, node_class: type[BaseNode] | type[BaseNebulaNode] | type[BaseModel] | None = None) -> list[BaseNode | BaseNebulaNode | BaseModel]:
        query = f"MATCH (n:{tag_name}) RETURN n"
        nodes = []
        with self.connector.session(name_space) as session:
            result = session.execute(query)
            for res in result.as_primitive():
                data = res["n"]["tags"]
                if node_class is None:
                    node_class = find_class_by_tag_name(tag_name)
                node = node_class(**data[tag_name])
                nodes.append(node)
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
