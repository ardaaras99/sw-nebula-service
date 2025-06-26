from datetime import datetime

from pydantic import BaseModel


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
    pdf_file_hash: str
    pdf_file_name: str
    lib_name: str
    ontology_name: str
    time_of_upload: datetime
    file_load_status: bool
    kg_extraction_status: bool


PREDEFINED_NODE_CLASSES = [
    RootNode,
    LibNode,
    OntologyNode,
    PdfNode,
]
