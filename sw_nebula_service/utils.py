from sw_onto_generation.utils import get_all_common_and_root_classes

from sw_nebula_service.models import PREDEFINED_EDGE_CLASSES, PREDEFINED_NODE_CLASSES


def pascal_case_to_snake_case(name: str) -> str:
    return "".join(["_" + i.lower() if i.isupper() else i for i in name]).lstrip("_")


NODE_CLASSES_WRITTEN, RELATION_CLASSES_WRITTEN = get_all_common_and_root_classes()
FULL_NODE_CLASSES = PREDEFINED_NODE_CLASSES + NODE_CLASSES_WRITTEN
FULL_EDGE_CLASSES = PREDEFINED_EDGE_CLASSES + RELATION_CLASSES_WRITTEN
