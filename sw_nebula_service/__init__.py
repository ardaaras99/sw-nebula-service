__version__ = "0.1.0"
from sw_onto_generation.utils import get_all_common_and_root_classes

from sw_nebula_service.models.nodes import PREDEFINED_NODE_CLASSES
from sw_nebula_service.models.relations import PREDEFINED_RELATION_CLASSES

WRITTEN_NODE_CLASSES, WRITTEN_RELATION_CLASSES = get_all_common_and_root_classes()
NODE_CLASSES = WRITTEN_NODE_CLASSES + PREDEFINED_NODE_CLASSES
RELATION_CLASSES = WRITTEN_RELATION_CLASSES + PREDEFINED_RELATION_CLASSES
