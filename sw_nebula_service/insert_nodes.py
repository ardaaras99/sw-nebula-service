from sw_onto_generation import DIR_STRUCTURE

from sw_nebula_service.engine import NebulaEngine
from sw_nebula_service.models import LibNode, OntologyNode, RootNode


def insert_directory_nodes(engine: NebulaEngine, name_space: str):
    node = RootNode(name="root")
    root_vid = engine.insert_node(name_space=name_space, node=node, vid=000)

    for i, lib_name in enumerate(DIR_STRUCTURE.keys()):
        lib_vid = engine.insert_node(
            name_space=name_space,
            node=LibNode(name=f"lib_{lib_name}"),
            vid=i,
        )
        engine.insert_edge_without_property(
            name_space=name_space,
            edge_type="has_lib",
            src_vid=root_vid,
            dst_vid=lib_vid,
        )
        for j, ontology_name in enumerate(DIR_STRUCTURE[lib_name]):
            ontology_vid = engine.insert_node(
                name_space=name_space,
                node=OntologyNode(name=f"onto_{ontology_name}"),
                vid=i + j,
            )
            engine.insert_edge_without_property(
                name_space=name_space,
                edge_type="has_ontology",
                src_vid=lib_vid,
                dst_vid=ontology_vid,
            )
