from pydantic import BaseModel
from sw_onto_generation.base.base_node import BaseNode
from sw_onto_generation.common.common_nodes import GeneralDocumentInfo

from sw_nebula_service.models.nodes import BaseNebulaNode, LibNode, OntologyNode, PdfNode, RootNode


class BaseNebulaRelation(BaseModel):
    source_node: BaseNebulaNode
    target_node: BaseNebulaNode | BaseNode


class HasLib(BaseNebulaRelation):
    source_node: RootNode
    target_node: LibNode


class HasOntology(BaseNebulaRelation):
    source_node: LibNode
    target_node: OntologyNode


class HasPdf(BaseNebulaRelation):
    source_node: OntologyNode
    target_node: PdfNode


class HasGeneralDocumentInfo(BaseNebulaRelation):
    source_node: PdfNode
    target_node: GeneralDocumentInfo


PREDEFINED_RELATION_CLASSES = [
    HasLib,
    HasOntology,
    HasPdf,
    HasGeneralDocumentInfo,
]
