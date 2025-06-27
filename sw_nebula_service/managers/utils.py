import types
from datetime import datetime
from typing import Any

from pydantic import BaseModel
from sw_onto_generation.base.base_node import BaseNode

from sw_nebula_service.models.nodes import BaseNebulaNode


class NebulaBooleanQueryResult(BaseModel):
    is_succeeded: bool
    message: str | None = None


TYPE_MAPPING = {
    int: "int",
    float: "float",
    str: "string",
    bool: "bool",
    datetime: "datetime",
}


def pascal_case_to_snake_case(name: str) -> str:
    return "".join(["_" + i.lower() if i.isupper() else i for i in name]).lstrip("_")


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
