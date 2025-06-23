# %%

import time

from rich import print as rprint

from sw_nebula_service.engine import Engine, EngineConfig
from sw_nebula_service.managers.connector import Connector, ConnectorConfig
from sw_nebula_service.managers.edge_manager import EdgeManager
from sw_nebula_service.managers.edge_type_manager import EdgeTypeManager
from sw_nebula_service.managers.space_manager import SpaceManager
from sw_nebula_service.managers.tag_manager import TagManager
from sw_nebula_service.managers.vertex_manager import VertexManager
from sw_nebula_service.models import PREDEFINED_EDGE_CLASSES, PREDEFINED_NODE_CLASSES

host = "192.168.3.70"
port = 32113
username = "root"
password = "nebula"
NAME_SPACE = "test_arda"

connector = Connector(ConnectorConfig(host=host, port=port, username=username, password=password))
engine_config = EngineConfig(
    connector=connector,
    space_manager=SpaceManager(connector=connector),
    tag_manager=TagManager(connector=connector),
    vertex_manager=VertexManager(connector=connector),
    edge_type_manager=EdgeTypeManager(connector=connector),
    edge_manager=EdgeManager(connector=connector),
)
engine = Engine(engine_config)
engine.space_manager.delete_all_namespaces()
engine.space_manager.create_namespace(
    NAME_SPACE,
    partition_num=100,
    replica_factor=1,
    vid_type="FIXED_STRING(256)",
)


engine.create_defined_schemas(NAME_SPACE, PREDEFINED_NODE_CLASSES, PREDEFINED_EDGE_CLASSES)

# %%


from hashlib import sha256
from uuid import uuid4

# Check how many bytes UUID4 stores
# UUID4 is 128 bits (16 bytes) but the string representation is longer
# %%

engine.insert_directory_nodes(NAME_SPACE)


def insert_n_random_nodes(engine: Engine, name_space: str, num_nodes: int):
    import random
    from datetime import datetime

    from sw_nebula_service.models import PdfNode

    for i in range(num_nodes):
        node = PdfNode(
            user_id=f"user_{i}",
            pdf_file_id=i,
            pdf_file_name=f"pdf_file_{i}",
            minio_bucket_path=f"minio_bucket_path_{i}",
            lib_name=f"lib_{i}",
            ontology_name=f"ontology_{i}",
            time_of_upload=datetime.now(),
            file_load_status=random.choice([True, False]),  # noqa: S311
            kg_extraction_status=random.choice([True, False]),  # noqa: S311
        )
        sha256_hash = sha256(node.model_dump_json().encode()).hexdigest()
        rprint(sha256_hash)
        # SHA-256 produces a 256-bit (32-byte) hash value
        # The hexdigest() returns a string with 64 hex characters (each byte = 2 hex chars)
        rprint(f"SHA-256 hash length: {len(sha256_hash)} hex chars = {len(sha256_hash) * 4} bits")
        rprint(f"Original SHA-256 size: 256 bits (32 bytes)")
        engine.vertex_manager.insert_vertex(name_space=name_space, node=node, vid=sha256_hash)
        engine.edge_manager.insert_edge_without_property(name_space=name_space, edge_type="has_pdf", src_vid="onto_kira", dst_vid=sha256_hash)


insert_n_random_nodes(engine, NAME_SPACE, 5)

# %%
