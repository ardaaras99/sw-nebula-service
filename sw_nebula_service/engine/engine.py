from contextlib import contextmanager
from typing import Any

from nebula3.Config import Config
from nebula3.gclient.net import ConnectionPool
from pydantic import BaseModel
from rich import print as rprint
from sw_onto_generation.base.base_relation import BaseRelation

from sw_nebula_service.engine.utils import format_field_value_for_nebula_graph, pascal_case_to_snake_case, pydantic_type_to_nebula_type, result_to_df
from sw_nebula_service.models import BaseNebulaRelation


class NebulaEngineConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str


class NebulaEngine:
    def __init__(self, config: NebulaEngineConfig):
        self.nebula_engine_config = config
        self.connection_pool = ConnectionPool()
        self.is_connected = False
        self.config = Config()
        self.config.max_connection_pool_size = 10

    def connect(self) -> bool:
        try:
            self.is_connected = self.connection_pool.init([(self.nebula_engine_config.host, self.nebula_engine_config.port)])  # noqa: S104
            if self.is_connected:
                rprint("Connected to Nebula Graph")
            else:
                rprint("Failed to connect to Nebula Graph")
            return self.is_connected
        except Exception as e:
            rprint(e)
            return False

    @contextmanager
    def session(self, name_space: str | None = None):
        if not self.is_connected:
            if not self.connect():
                raise ConnectionError("Cannot establish connection to Nebula Graph")
        session = None
        try:
            session = self.connection_pool.get_session(self.nebula_engine_config.username, self.nebula_engine_config.password)
            if name_space:
                result = session.execute(f"USE {name_space}")
                if not result.is_succeeded():
                    raise Exception(f"Failed to use namespace {name_space}: {result.error_msg()}")
            yield session
        finally:
            if session:
                session.release()

    def create_namespace(self, name_space: str, partition_num: int = 100, replica_factor: int = 1) -> bool:
        with self.session() as session:
            query = f"""
            CREATE SPACE IF NOT EXISTS {name_space} (
                partition_num = {partition_num},
                replica_factor = {replica_factor},
                vid_type = FIXED_STRING(32)
            )
            """
            result = session.execute(query)
            if result.is_succeeded():
                return True
            else:
                raise Exception(f"Failed to create namespace {name_space}: {result.error_msg()}")

    def create_tag_from_pydantic(self, name_space: str, model_class: type[BaseModel]) -> str:
        tag_name = pascal_case_to_snake_case(model_class.__name__)
        fields = []
        for field_name, field_info in model_class.model_fields.items():
            nebula_type = pydantic_type_to_nebula_type(field_info.annotation)
            fields.append(f"{field_name} {nebula_type}")

        if not fields:
            raise ValueError(f"No fields found for tag {tag_name} from {model_class.__name__}")

        query = f"CREATE TAG IF NOT EXISTS {tag_name} ({', '.join(fields)})"
        # rprint(f"query: {query}")
        with self.session(name_space) as session:
            result = session.execute(query)
            if result.is_succeeded():
                # get tags in namespace
                tags = session.execute("SHOW TAGS").rows()
                for tag in tags:
                    to_check = tag.values[0].value.decode("utf-8")
                    if tag_name in to_check:
                        rprint(f"Tag {tag_name} created successfully")
                        return tag_name
            else:
                raise Exception(f"Failed to create tag {tag_name}: {result.error_msg()}")

    def insert_node(self, name_space: str, node: BaseModel) -> bool:
        data = node.model_dump()
        tag_name = pascal_case_to_snake_case(node.__class__.__name__)
        formatted_data = []
        for field_name in list(data.keys()):
            value = data.get(field_name)
            formatted_data.append(format_field_value_for_nebula_graph(value))
        values_str = ", ".join(formatted_data)
        query = f'INSERT VERTEX IF NOT EXISTS {tag_name} VALUES "{node.vid}": ({values_str})'  # noqa: S608
        rprint(f"query: {query}")
        with self.session(name_space) as session:
            max_retries = 10
            retry_count = 0
            retry_delay = 1  # seconds
            import time

            while retry_count < max_retries:
                result = session.execute(query)
                if result.is_succeeded():
                    rprint(f"Node {node.vid} inserted successfully")
                    return node.vid
                else:
                    retry_count += 1
                    if retry_count < max_retries:
                        rprint(f"Attempt {retry_count} failed. Trying to run query {query}. Retrying in {retry_delay} seconds..., error: {result.error_msg()}")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        raise Exception(f"Failed to insert node instance for tag {tag_name} after {max_retries} attempts: {result.error_msg()}")

    def read_nodes(self, name_space: str, tag_name: str, response_model: type[BaseModel]) -> list[BaseModel]:
        nodes = []
        with self.session(name_space) as session:
            query = f"MATCH (n:{tag_name}) RETURN n"
            rprint(f"query: {query}")
            result = session.execute(query)
            result_df = result_to_df(result)
            for node in result_df["n"]:
                node_properties = node.properties()
                fields = {}
                for field_name, _ in response_model.model_fields.items():
                    fields[field_name] = node_properties[field_name].cast()
                nodes.append(response_model(**fields))
        return nodes

    def update_node_field(self, name_space: str, tag_name: str, node_id: str, field_name: str, value: Any) -> bool:
        with self.session(name_space) as session:
            query = f'UPDATE VERTEX ON {tag_name} "{node_id}" SET {field_name} = {value}'  # noqa: S608
            result = session.execute(query)
            rprint(f"query: {query}")
            if result.is_succeeded():
                return True
            else:
                raise Exception(f"Failed to update node field value for tag {tag_name}: {result.error_msg()}")

    def create_tag_index(self, name_space: str, tag_name: str, index_name: str) -> bool:
        with self.session(name_space) as session:
            query = f"CREATE TAG INDEX IF NOT EXISTS {index_name} ON {tag_name}()"
            result = session.execute(query)
            if result.is_succeeded():
                return True
            else:
                raise Exception(f"Failed to create index {index_name} for tag {tag_name}: {result.error_msg()}")

    def create_edge_index(self, name_space: str, edge_type: str, index_name: str) -> bool:
        with self.session(name_space) as session:
            query = f"CREATE EDGE INDEX IF NOT EXISTS {index_name} ON {edge_type}()"
            result = session.execute(query)
            if result.is_succeeded():
                return True
            else:
                raise Exception(f"Failed to create index {index_name} for edge type {edge_type}: {result.error_msg()}")

    def create_index_on_tag_property(
        self,
        name_space: str,
        tag_name: str,
        index_name: str,
        property_name: str,
        index_length: int = 100,
    ) -> bool:
        with self.session(name_space) as session:
            query = f"CREATE TAG INDEX IF NOT EXISTS {index_name} ON {tag_name}({property_name}({index_length}))"
            result = session.execute(query)
            if result.is_succeeded():
                return True
            else:
                raise Exception(f"Failed to create index {index_name} for tag {tag_name}: {result.error_msg()}")

    def delete_all_namespaces(self) -> bool:
        with self.session() as session:
            query = "SHOW SPACES"
            result = session.execute(query)
            for space in result.rows():
                space_name = space.values[0].value.decode("utf-8")
                query = f"DROP SPACE {space_name}"
                result = session.execute(query)

    def create_edge_type_without_property(self, name_space: str, edge_class: type[BaseNebulaRelation]) -> bool:
        edge_type = pascal_case_to_snake_case(edge_class.__name__)
        with self.session(name_space) as session:
            query = f"CREATE EDGE IF NOT EXISTS {edge_type}()"
            result = session.execute(query)
            if result.is_succeeded():
                return True
            else:
                raise Exception(f"Failed to create edge type {edge_type}: {result.error_msg()}")

    def create_edge_type_with_property(self, name_space: str, edge_class: type[BaseRelation] | type[BaseNebulaRelation]) -> bool:
        edge_type = pascal_case_to_snake_case(edge_class.__name__)
        with self.session(name_space) as session:
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
                return True
            else:
                raise Exception(f"Failed to create edge type {edge_type}: {result.error_msg()}")

    def insert_edge_without_property(self, name_space: str, edge_type: str, src_vid: str, dst_vid: str) -> bool:
        with self.session(name_space) as session:
            query = f'INSERT EDGE IF NOT EXISTS {edge_type} () VALUES "{src_vid}"->"{dst_vid}":()'  # noqa: S608
            rprint(f"Inserting edge {edge_type} from {src_vid} -> {dst_vid}")
            result = session.execute(query)
            if result.is_succeeded():
                return True
            else:
                raise Exception(f"Failed to insert edge type {edge_type}: {result.error_msg()}")
