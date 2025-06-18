# %%


import importlib
import inspect
import pkgutil
from types import ModuleType

from rich import print as rprint
from sw_onto_generation.base.base_node import BaseNode
from sw_onto_generation.base.base_relation import BaseRelation

from sw_nebula_service.engine.engine import NebulaEngine, NebulaEngineConfig
from sw_nebula_service.models import PREDEFINED_EDGE_CLASSES, PREDEFINED_NODE_CLASSES, BaseNebulaNode, BaseNebulaRelation


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


def _find_node_classes_in_module(module: ModuleType) -> list[type[BaseNode]]:
    """Find all classes in the module that inherit from BaseNode."""
    node_classes = []

    for name, obj in inspect.getmembers(module):
        # Check if it's a class and inherits from BaseNode
        if inspect.isclass(obj) and issubclass(obj, BaseNode) and obj != BaseNode:
            node_classes.append(obj)

    return node_classes


def _find_relation_classes_in_module(module: ModuleType) -> list[type[BaseRelation]]:
    """Find all classes in the module that inherit from BaseRelation."""
    relation_classes = []

    for name, obj in inspect.getmembers(module):
        # Check if it's a class and inherits from BaseRelation
        if inspect.isclass(obj) and issubclass(obj, BaseRelation) and obj != BaseRelation:
            relation_classes.append(obj)

    return relation_classes


def _import_submodules(package_name: str) -> list[ModuleType]:
    """Import all submodules of a package recursively."""
    package = importlib.import_module(package_name)
    results = [package]

    if hasattr(package, "__path__"):
        for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
            try:
                results.append(importlib.import_module(name))
                if is_pkg:
                    results.extend(_import_submodules(name))
            except ImportError as e:
                rprint(f"Error importing {name}: {e}")

    return results


def get_node_classes_from_onto_generation() -> list[type[BaseNode]]:
    # We need to search in all submodules under root and common
    node_module_names = ["sw_onto_generation.common", "sw_onto_generation.root"]
    node_classes = set()  # Use a set to avoid duplicates

    for module_name in node_module_names:
        try:
            rprint(f"Importing {module_name} and all its submodules...")
            modules = _import_submodules(module_name)
            rprint(f"Successfully imported {len(modules)} modules from {module_name}")

            for module in modules:
                module_node_classes = _find_node_classes_in_module(module)
                node_classes.update(module_node_classes)
        except Exception as e:
            rprint(f"Error processing {module_name}: {str(e)}")

    # Print found classes after deduplication
    rprint("Found node classes:")
    for cls in node_classes:
        rprint(f"  - {cls.__name__} in {cls.__module__}")

    return list(node_classes)


def get_relation_classes_from_onto_generation() -> list[type[BaseRelation]]:
    relation_module_names = ["sw_onto_generation.common", "sw_onto_generation.root"]
    relation_classes = set()  # Use a set to avoid duplicates

    for module_name in relation_module_names:
        try:
            rprint(f"Importing {module_name} and all its submodules...")
            modules = _import_submodules(module_name)
            rprint(f"Successfully imported {len(modules)} modules from {module_name}")

            for module in modules:
                module_relation_classes = _find_relation_classes_in_module(module)
                relation_classes.update(module_relation_classes)
        except Exception as e:
            rprint(f"Error processing {module_name}: {str(e)}")

    # Print found classes after deduplication
    rprint("Found relation classes:")
    for cls in relation_classes:
        rprint(f"  - {cls.__name__} in {cls.__module__}")

    return list(relation_classes)


if __name__ == "__main__":
    engine = NebulaEngine(config=NebulaEngineConfig(host="0.0.0.0", port=9669, username="root", password="nebula"))  # noqa: S106

    node_classes_from_onto_generation = get_node_classes_from_onto_generation()
    rprint(f"Total node classes found: {len(node_classes_from_onto_generation)}")
    relation_classes_from_onto_generation = get_relation_classes_from_onto_generation()
    rprint(f"Total relation classes found: {len(relation_classes_from_onto_generation)}")

    # Create schemas
    node_classes = PREDEFINED_NODE_CLASSES + node_classes_from_onto_generation
    relation_classes = PREDEFINED_EDGE_CLASSES + relation_classes_from_onto_generation
    create_full_schemas(engine=engine, name_space="knowledge_graph", node_classes=node_classes, relation_classes=relation_classes)

# %%
