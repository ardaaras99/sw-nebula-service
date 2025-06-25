from rich import print as rprint

from sw_nebula_service.managers.connector import Connector


class SpaceManager:
    def __init__(self, connector: Connector):
        self.connector = connector

    def create_namespace(self, name_space: str, partition_num: int = 100, replica_factor: int = 1, vid_type: str = "INT64") -> bool:
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
                return True
            else:
                raise Exception(f"Failed to create space {name_space}: {result.error_msg()}")

    def delete_all_namespaces(self) -> bool:
        with self.connector.session() as session:
            query = "SHOW SPACES"
            result = session.execute(query)
            for space in result.rows():
                space_name = space.values[0].value.decode("utf-8")
                query = f"DROP SPACE {space_name}"
                result = session.execute(query)

    def delete_namespace(self, name_space: str) -> bool:
        with self.connector.session() as session:
            query = f"DROP SPACE {name_space}"
            result = session.execute(query)
            if result.is_succeeded():
                return True
            else:
                rprint(f"Failed to delete space {name_space}: {result.error_msg()}")
