from rich import print as rprint
from sw_onto_generation.base.base_relation import BaseRelation

from sw_nebula_service.managers.connector import Connector
from sw_nebula_service.managers.utils import NebulaBooleanQueryResult, pascal_case_to_snake_case
from sw_nebula_service.models.relations import BaseNebulaRelation


class EdgeTypeManager:
    def __init__(self, connector: Connector):
        self.connector = connector

    def create_edge_type_without_property(self, name_space: str, edge_class: type[BaseNebulaRelation]) -> NebulaBooleanQueryResult:
        edge_type = pascal_case_to_snake_case(edge_class.__name__)
        with self.connector.session(name_space) as session:
            query = f"CREATE EDGE IF NOT EXISTS {edge_type}()"
            result = session.execute(query)
            if result.is_succeeded():
                return NebulaBooleanQueryResult(is_succeeded=True, message=f"Successfully created edge type {edge_type}")
            else:
                return NebulaBooleanQueryResult(is_succeeded=False, message=f"Failed to create edge type {edge_type}: {result.error_msg()}")

    def create_edge_type_with_property(self, name_space: str, edge_class: type[BaseRelation] | type[BaseNebulaRelation]) -> NebulaBooleanQueryResult:
        edge_type = pascal_case_to_snake_case(edge_class.__name__)
        with self.connector.session(name_space) as session:
            import types

            source_annotation = edge_class.model_fields["source_node"].annotation
            target_annotation = edge_class.model_fields["target_node"].annotation

            if isinstance(source_annotation, types.UnionType):
                source_default = f"{source_annotation.__args__[0].__name__} | {source_annotation.__args__[1].__name__}"
            else:
                source_default = source_annotation.__name__

            if isinstance(target_annotation, types.UnionType):
                target_default = f"{target_annotation.__args__[0].__name__} | {target_annotation.__args__[1].__name__}"
            else:
                target_default = target_annotation.__name__

            rprint(f"source_default: {source_default}, target_default: {target_default}")

            query = f'CREATE EDGE IF NOT EXISTS {edge_type}(source_node string DEFAULT "{source_default}", target_node string DEFAULT "{target_default}")'  # noqa: S608
            rprint(f"query: {query}")
            result = session.execute(query)
            if result.is_succeeded():
                return NebulaBooleanQueryResult(is_succeeded=True, message=f"Successfully created edge type {edge_type}")
            else:
                return NebulaBooleanQueryResult(is_succeeded=False, message=f"Failed to create edge type {edge_type}: {result.error_msg()}")

    def create_edge_type_index(self, name_space: str, edge_type: str, index_name: str) -> NebulaBooleanQueryResult:
        with self.connector.session(name_space) as session:
            query = f"CREATE EDGE INDEX IF NOT EXISTS {index_name} ON {edge_type}()"
            result = session.execute(query)
            if result.is_succeeded():
                return NebulaBooleanQueryResult(is_succeeded=True, message=f"Successfully created index {index_name} for edge type {edge_type}")
            else:
                return NebulaBooleanQueryResult(is_succeeded=False, message=f"Failed to create index {index_name} for edge type {edge_type}: {result.error_msg()}")
