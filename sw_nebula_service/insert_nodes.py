# %%

from sw_onto_generation import ENUM_CLASSES

from sw_nebula_service.engine.engine import NebulaEngine, NebulaEngineConfig
from sw_nebula_service.models import LibNode, OntologyNode, RootNode


def insert_directory_nodes(engine: NebulaEngine):
    d = {lib.__name__: [member.value for member in lib] for lib in ENUM_CLASSES}

    name_space = "knowledge_graph"

    node = RootNode(vid="root", name="root")
    root_vid = engine.insert_node(name_space=name_space, node=node)

    for lib_name in list(d.keys()):
        lib_vid = engine.insert_node(name_space=name_space, node=LibNode(vid=lib_name, name=f"lib_{lib_name}"))
        engine.insert_edge_without_property(name_space=name_space, edge_type="has_lib", src_vid=root_vid, dst_vid=lib_vid)
        for ontology_name in d[lib_name]:
            ontology_vid = engine.insert_node(name_space=name_space, node=OntologyNode(vid=ontology_name, name=f"onto_{ontology_name}"))
            engine.insert_edge_without_property(name_space=name_space, edge_type="has_ontology", src_vid=lib_vid, dst_vid=ontology_vid)


if __name__ == "__main__":
    engine = NebulaEngine(config=NebulaEngineConfig(host="0.0.0.0", port=9669, username="root", password="nebula"))
    insert_directory_nodes(engine=engine)

# %%
