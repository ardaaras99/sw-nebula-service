from pydantic import BaseModel
from sw_onto_generation import DIR_STRUCTURE
from sw_onto_generation.base.base_node import BaseNode
from sw_onto_generation.base.base_relation import BaseRelation

from sw_nebula_service.managers.connector import Connector
from sw_nebula_service.managers.edge_manager import EdgeManager
from sw_nebula_service.managers.edge_type_manager import EdgeTypeManager
from sw_nebula_service.managers.space_manager import SpaceManager
from sw_nebula_service.managers.tag_manager import TagManager
from sw_nebula_service.managers.vertex_manager import VertexManager
from sw_nebula_service.models import BaseNebulaNode, BaseNebulaRelation, LibNode, OntologyNode, RootNode


class EngineConfig(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    connector: Connector


class Engine:
    def __init__(self, config: EngineConfig):
        self.connector = config.connector
        self.space_manager = SpaceManager(self.connector)
        self.tag_manager = TagManager(self.connector)
        self.vertex_manager = VertexManager(self.connector)
        self.edge_type_manager = EdgeTypeManager(self.connector)
        self.edge_manager = EdgeManager(self.connector)

    def create_defined_schemas(self, name_space: str, node_classes: list[type[BaseNode] | type[BaseNebulaNode]], relation_classes: list[type[BaseRelation] | type[BaseNebulaRelation]]):
        self.space_manager.create_namespace(name_space=name_space)
        for node in node_classes:
            self.tag_manager.create_tag(name_space=name_space, node_class=node)
        for relation in relation_classes:
            self.edge_type_manager.create_edge_type_with_property(name_space=name_space, edge_class=relation)

    def insert_directory_nodes(self, name_space: str):
        node = RootNode(name="root")
        self.vertex_manager.insert_vertex(name_space=name_space, node=node, vid="root")
        for i, lib_name in enumerate(DIR_STRUCTURE.keys(), start=1):
            self.vertex_manager.insert_vertex(
                name_space=name_space,
                node=LibNode(name=f"lib_{lib_name}"),
                vid=f"lib_{lib_name}",
            )
            self.edge_manager.insert_edge_without_property(
                name_space=name_space,
                edge_type="has_lib",
                src_vid="root",
                dst_vid=f"lib_{lib_name}",
            )
            for j, ontology_name in enumerate(DIR_STRUCTURE[lib_name], start=i + 1):
                self.vertex_manager.insert_vertex(
                    name_space=name_space,
                    node=OntologyNode(name=f"onto_{ontology_name}"),
                    vid=f"onto_{ontology_name}",
                )
                self.edge_manager.insert_edge_without_property(
                    name_space=name_space,
                    edge_type="has_ontology",
                    src_vid=f"lib_{lib_name}",
                    dst_vid=f"onto_{ontology_name}",
                )
