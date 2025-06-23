import types
from datetime import datetime

from pydantic import BaseModel
from rich import print as rprint
from sw_onto_generation.base.base_node import BaseNode

from sw_nebula_service.managers.connector import Connector
from sw_nebula_service.models import BaseNebulaNode
from sw_nebula_service.utils import pascal_case_to_snake_case

TYPE_MAPPING = {
    int: "int",
    float: "float",
    str: "string",
    bool: "bool",
    datetime: "datetime",
}


def convert_fields_of_class_to_nebula_types(node_class: type[BaseNode] | type[BaseNebulaNode] | type[BaseModel]) -> str:
    fields = []
    for field_name, field_info in node_class.model_fields.items():
        # rprint(f"field_info.annotation: {field_info.annotation}")
        if field_info.annotation is None:
            raise ValueError(f"field_name: {field_name} is None")
        #! BaseModel check added to skip like Adres inside of Insan
        elif isinstance(field_info.annotation, types.UnionType):
            args = getattr(field_info.annotation, "__args__", ())
            for arg in args:
                if arg is type(None):
                    continue
                elif issubclass(arg, BaseModel):
                    continue
                else:
                    possible_type = arg
        elif issubclass(field_info.annotation, BaseModel):
            continue
        else:
            possible_type = field_info.annotation
        fields.append(f"{field_name} {TYPE_MAPPING.get(possible_type)}")
    return fields


class TagManager:
    def __init__(self, connector: Connector):
        self.connector = connector

    def create_tag(self, name_space: str, node_class: type[BaseNode] | type[BaseNebulaNode] | type[BaseModel]) -> str:
        tag_name = pascal_case_to_snake_case(node_class.__name__)
        fields = convert_fields_of_class_to_nebula_types(node_class)
        query = f"CREATE TAG IF NOT EXISTS {tag_name} ({', '.join(fields)})"
        with self.connector.session(name_space) as session:
            result = session.execute(query)
            if result.is_succeeded():
                rprint(f"Tag {tag_name} created successfully")
            else:
                rprint(f"Failed query: {query}")
                raise Exception(f"Failed to create tag {tag_name}: {result.error_msg()}")

    def create_tag_index(self, name_space: str, tag_name: str, index_name: str) -> bool:
        with self.connector.session(name_space) as session:
            query = f"CREATE TAG INDEX IF NOT EXISTS {index_name} ON {tag_name}()"
            result = session.execute(query)
            if result.is_succeeded():
                return True
            else:
                raise Exception(f"Failed to create index {index_name} for tag {tag_name}: {result.error_msg()}")

    def create_index_on_tag_property(self, name_space: str, tag_name: str, index_name: str, property_name: str, index_length: int = 100) -> bool:
        with self.connector.session(name_space) as session:
            query = f"CREATE TAG INDEX IF NOT EXISTS {index_name} ON {tag_name}({property_name}({index_length}))"
            result = session.execute(query)
            if result.is_succeeded():
                return True
            else:
                raise Exception(f"Failed to create index {index_name} for tag {tag_name}: {result.error_msg()}")
