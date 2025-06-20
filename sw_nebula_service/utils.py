import json
from datetime import datetime
from typing import Any

import pandas as pd
from nebula3.data.ResultSet import ResultSet


def pascal_case_to_snake_case(name: str) -> str:
    return "".join(["_" + i.lower() if i.isupper() else i for i in name]).lstrip("_")


def pydantic_type_to_nebula_type(field_type: type) -> str:
    type_mapping = {
        int: "int",
        float: "float",
        str: "string",
        bool: "bool",
        list: "string",  # Store as JSON string
        dict: "string",  # Store as JSON string
        datetime: "timestamp",
    }

    # Handle Union types (Optional)
    origin = getattr(field_type, "__origin__", None)
    if origin is not None:
        args = getattr(field_type, "__args__", ())
        if origin is list and args:
            return "string"  # Store lists as JSON strings
        # For Union types (like Optional), use the first non-None type
        non_none_types = [arg for arg in args if arg is not type(None)]
        if non_none_types:
            field_type = non_none_types[0]

    return type_mapping.get(field_type, "string")


def format_field_value_for_nebula_graph(value: Any) -> str:
    if isinstance(value, datetime):
        # return f'timestamp("{value.strftime("%Y-%m-%dT%H:%M:%S")}")'
        return "now"
    elif isinstance(value, list | dict):
        return f'"{json.dumps(value)}"'
    elif value is None:
        return "NULL"
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, int):
        return str(value)
    else:
        return f'"{str(value)}"'


def result_to_df(result: ResultSet) -> pd.DataFrame:
    """
    build list for each column, and transform to dataframe
    """
    columns = result.keys()
    d: dict[str, list] = {}
    for col_num in range(result.col_size()):
        col_name = columns[col_num]
        col_list = result.column_values(col_name)
        d[col_name] = [x.cast() for x in col_list]
    return pd.DataFrame.from_dict(d)
