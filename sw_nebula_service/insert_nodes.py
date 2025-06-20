from sw_onto_generation import DIR_STRUCTURE

from sw_nebula_service.engine import NebulaEngine
from sw_nebula_service.models import LibNode, OntologyNode, RootNode


def insert_directory_nodes(engine: NebulaEngine, name_space: str):
    node = RootNode(name="root")
    root_vid = engine.insert_node(name_space=name_space, node=node, vid="root")

    for lib_name in DIR_STRUCTURE.keys():
        lib_vid = engine.insert_node(name_space=name_space, node=LibNode(name=f"lib_{lib_name}"), vid=f"lib_{lib_name}")
        engine.insert_edge_without_property(name_space=name_space, edge_type="has_lib", src_vid=root_vid, dst_vid=lib_vid)
        for ontology_name in DIR_STRUCTURE[lib_name]:
            ontology_vid = engine.insert_node(name_space=name_space, node=OntologyNode(name=f"onto_{ontology_name}"), vid=f"onto_{ontology_name}")
            engine.insert_edge_without_property(name_space=name_space, edge_type="has_ontology", src_vid=lib_vid, dst_vid=ontology_vid)
