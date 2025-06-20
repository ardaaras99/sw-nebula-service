from datetime import datetime

from pydantic import BaseModel
from sw_onto_generation.base.base_node import BaseNode
from sw_onto_generation.common.common_nodes import GeneralDocumentInfo


class BaseNebulaNode(BaseModel):
    pass


class RootNode(BaseNebulaNode):
    name: str


class LibNode(BaseNebulaNode):
    name: str


class OntologyNode(BaseNebulaNode):
    name: str


class PdfNode(BaseNebulaNode):
    user_id: str
    pdf_file_id: int
    pdf_file_name: str
    minio_bucket_path: str

    lib_name: str
    ontology_name: str

    time_of_upload: datetime
    file_load_status: bool
    kg_extraction_status: bool


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


PREDEFINED_NODE_CLASSES = [RootNode, LibNode, OntologyNode, PdfNode]
PREDEFINED_EDGE_CLASSES = [HasLib, HasOntology, HasPdf, HasGeneralDocumentInfo]
