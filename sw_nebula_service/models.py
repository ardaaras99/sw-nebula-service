from datetime import datetime

from pydantic import BaseModel


class BaseNebulaNode(BaseModel):
    vid: str


class RootNode(BaseNebulaNode):
    name: str


class LibNode(BaseNebulaNode):
    name: str


class OntologyNode(BaseNebulaNode):
    name: str


class PdfNode(BaseNebulaNode):
    file_name: str
    minio_bucket_path: str
    document_lib: str
    document_type: str
    user_id: str
    time_of_upload: datetime
    file_load_status: bool
    kg_extraction_status: bool


class BaseNebulaRelation(BaseModel):
    source_node: BaseNebulaNode
    target_node: BaseNebulaNode


class HasLib(BaseNebulaRelation):
    source_node: RootNode
    target_node: LibNode


class HasOntology(BaseNebulaRelation):
    source_node: LibNode
    target_node: OntologyNode


class HasPdf(BaseNebulaRelation):
    source_node: OntologyNode
    target_node: PdfNode


PREDEFINED_NODE_CLASSES = [RootNode, LibNode, OntologyNode, PdfNode]
PREDEFINED_EDGE_CLASSES = [HasLib, HasOntology, HasPdf]
