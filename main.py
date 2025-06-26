# %%




from sw_nebula_service.engine import Engine, EngineConfig
from sw_nebula_service.managers.connector import Connector, ConnectorConfig
from sw_nebula_service.utils import FULL_NODE_CLASSES, pascal_case_to_snake_case

NAME_SPACE = "kg_arda"


def tag_name_to_class(tag_name: str):
    for node_class in FULL_NODE_CLASSES:
        if pascal_case_to_snake_case(node_class.__name__) == tag_name:
            return node_class


connector = Connector(ConnectorConfig(host="192.168.3.70", port=32113, username="root", password="nebula"))
engine = Engine(EngineConfig(connector=connector))
tag_name = "insan"
engine.vertex_manager.get_vertex(name_space=NAME_SPACE, tag_name=tag_name, node_class=tag_name_to_class(tag_name))

# %%

# def insert_n_random_nodes(engine: Engine, name_space: str, num_nodes: int):
#     import random
#     from datetime import datetime

#     from sw_nebula_service.models import PdfNode

#     for i in range(num_nodes):
#         node = PdfNode(
#             user_id=f"user_{i}",
#             pdf_file_hash=i,
#             pdf_file_name=f"pdf_file_{i}",
#             minio_bucket_path=f"minio_bucket_path_{i}",
#             lib_name=f"lib_{i}",
#             ontology_name=f"ontology_{i}",
#             time_of_upload=datetime.now(),
#             file_load_status=random.choice([True, False]),  # noqa: S311
#             kg_extraction_status=random.choice([True, False]),  # noqa: S311
#         )
#         sha256_hash = sha256(node.model_dump_json().encode()).hexdigest()
#         rprint(sha256_hash)
#         # SHA-256 produces a 256-bit (32-byte) hash value
#         # The hexdigest() returns a string with 64 hex characters (each byte = 2 hex chars)
#         rprint(f"SHA-256 hash length: {len(sha256_hash)} hex chars = {len(sha256_hash) * 4} bits")
#         rprint(f"Original SHA-256 size: 256 bits (32 bytes)")
#         engine.vertex_manager.insert_vertex(name_space=name_space, node=node, vid=sha256_hash)
#         engine.edge_manager.insert_edge_without_property(name_space=name_space, edge_type="has_pdf", src_vid="onto_kira", dst_vid=sha256_hash)


# insert_n_random_nodes(engine, NAME_SPACE, 5)

# # %%
