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
    # Metadata
    user_id: str
    node_id: str
    pdf_file_hash: str
    pdf_file_name: str
    time_of_upload: datetime
    file_load_status: bool
    kg_extraction_status: bool

    # AI generated
    ai_lib_name: str
    ai_ontology_name: str
    ai_reasoning_for_classification: str

    # User chosen
    user_chosen_lib_name: str
    user_chosen_ontology_name: str


PREDEFINED_NODE_CLASSES = [
    RootNode,
    LibNode,
    OntologyNode,
    PdfNode,
]
