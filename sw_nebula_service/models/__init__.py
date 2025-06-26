from sw_nebula_service.models.nodes import LibNode, OntologyNode, PdfNode, RootNode
from sw_nebula_service.models.relations import HasLib, HasOntology, HasPdf

PREDEFINED_NODE_CLASSES = [
    RootNode,
    LibNode,
    OntologyNode,
    PdfNode,
]

PREDEFINED_RELATION_CLASSES = [
    HasLib,
    HasOntology,
    HasPdf,
]
