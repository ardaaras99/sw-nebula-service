from rich import print as rprint

from sw_nebula_service.managers.connector import Connector


class EdgeManager:
    def __init__(self, connector: Connector):
        self.connector = connector

    def insert_edge_without_property(self, name_space: str, edge_type: str, src_vid: str, dst_vid: str) -> bool:
        with self.connector.session(name_space) as session:
            query = f'INSERT EDGE IF NOT EXISTS {edge_type} () VALUES "{src_vid}"->"{dst_vid}":()'  # noqa: S608
            rprint(f"query: {query}")
            result = session.execute(query)
            if result.is_succeeded():
                return True
            else:
                raise Exception(f"Failed to insert edge type {edge_type}: {result.error_msg()}")
