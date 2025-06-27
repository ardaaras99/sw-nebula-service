from pydantic import BaseModel
from sw_onto_generation.base.base_node import BaseNode

from sw_nebula_service.managers.connector import Connector
from sw_nebula_service.managers.utils import NebulaBooleanQueryResult, convert_fields_of_class_to_nebula_types, pascal_case_to_snake_case
from sw_nebula_service.models.nodes import BaseNebulaNode


class TagManager:
    def __init__(self, connector: Connector):
        self.connector = connector

    def create_tag(self, name_space: str, node_class: type[BaseNode] | type[BaseNebulaNode] | type[BaseModel]) -> NebulaBooleanQueryResult:
        tag_name = pascal_case_to_snake_case(node_class.__name__)
        fields = convert_fields_of_class_to_nebula_types(node_class)
        query = f"CREATE TAG IF NOT EXISTS {tag_name} ({', '.join(fields)})"
        with self.connector.session(name_space) as session:
            result = session.execute(query)
            if result.is_succeeded():
                return NebulaBooleanQueryResult(is_succeeded=True, message=f"Successfully created tag {tag_name}")
            else:
                return NebulaBooleanQueryResult(is_succeeded=False, message=f"Failed to create tag {tag_name}: {result.error_msg()}")

    def create_tag_index(self, name_space: str, tag_name: str, index_name: str) -> NebulaBooleanQueryResult:
        with self.connector.session(name_space) as session:
            query = f"CREATE TAG INDEX IF NOT EXISTS {index_name} ON {tag_name}()"
            result = session.execute(query)
            if result.is_succeeded():
                return NebulaBooleanQueryResult(is_succeeded=True, message=f"Successfully created index {index_name} for tag {tag_name}")
            else:
                return NebulaBooleanQueryResult(is_succeeded=False, message=f"Failed to create index {index_name} for tag {tag_name}: {result.error_msg()}")

    def create_index_on_tag_property(self, name_space: str, tag_name: str, index_name: str, property_name: str, index_length: int = 100) -> NebulaBooleanQueryResult:
        with self.connector.session(name_space) as session:
            query = f"CREATE TAG INDEX IF NOT EXISTS {index_name} ON {tag_name}({property_name}({index_length}))"
            result = session.execute(query)
            if result.is_succeeded():
                return NebulaBooleanQueryResult(is_succeeded=True, message=f"Successfully created index {index_name} for tag {tag_name}")
            else:
                return NebulaBooleanQueryResult(is_succeeded=False, message=f"Failed to create index {index_name} for tag {tag_name}: {result.error_msg()}")

    def get_all_tags(self, name_space: str) -> list[str]:
        with self.connector.session(name_space) as session:
            tags = []
            result = session.execute("SHOW TAGS")
            if result.is_succeeded():
                for res in result.as_primitive():
                    tags.append(res["Name"])
                return tags
            else:
                raise Exception(f"Failed to get all tags: {result.error_msg()}")

    def drop_tag(self, name_space: str, tag_name: str) -> NebulaBooleanQueryResult:
        with self.connector.session(name_space) as session:
            query = f"DROP TAG IF EXISTS {tag_name}"
            result = session.execute(query)
            if result.is_succeeded():
                return NebulaBooleanQueryResult(is_succeeded=True, message=f"Successfully dropped tag {tag_name}")
            else:
                return NebulaBooleanQueryResult(is_succeeded=False, message=f"Failed to drop tag {tag_name}: {result.error_msg()}")
