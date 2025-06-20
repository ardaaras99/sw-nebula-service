# %%

from sw_onto_generation.common.common_nodes import BaseNode
from sw_onto_generation.common.common_relations import BaseRelation

from sw_nebula_service.engine import NebulaEngine
from sw_nebula_service.models import BaseNebulaNode, BaseNebulaRelation


def create_full_schemas(
    engine: NebulaEngine,
    name_space: str,
    node_classes: list[type[BaseNode] | type[BaseNebulaNode]],
    relation_classes: list[type[BaseRelation] | type[BaseNebulaRelation]],
):
    engine.delete_all_namespaces()
    engine.create_namespace(name_space=name_space)
    for node in node_classes:
        engine.create_tag_from_pydantic(name_space=name_space, model_class=node)

    for edge in relation_classes:
        engine.create_edge_type_with_property(name_space=name_space, edge_class=edge)


# %%
