from sw_nebula_service.managers.connector import Connector
from sw_nebula_service.managers.utils import NebulaBooleanQueryResult


class SpaceManager:
    def __init__(self, connector: Connector):
        self.connector = connector

    def create_namespace(self, name_space: str, partition_num: int = 100, replica_factor: int = 1, vid_type: str = "INT64") -> NebulaBooleanQueryResult:
        with self.connector.session() as session:
            query = f"""
            CREATE SPACE IF NOT EXISTS {name_space} (
                partition_num = {partition_num},
                replica_factor = {replica_factor},
                vid_type = {vid_type}
            )
            """
            result = session.execute(query)
            if result.is_succeeded():
                return NebulaBooleanQueryResult(is_succeeded=True, message=f"Successfully created space {name_space}")
            else:
                return NebulaBooleanQueryResult(is_succeeded=False, message=f"Failed to create space {name_space}: {result.error_msg()}")

    def delete_namespace(self, name_space: str) -> NebulaBooleanQueryResult:
        with self.connector.session() as session:
            query = f"DROP SPACE {name_space}"
            result = session.execute(query)
            if result.is_succeeded():
                return NebulaBooleanQueryResult(is_succeeded=True, message=f"Successfully deleted space {name_space}")
            else:
                return NebulaBooleanQueryResult(is_succeeded=False, message=f"Failed to delete space {name_space}: {result.error_msg()}")
