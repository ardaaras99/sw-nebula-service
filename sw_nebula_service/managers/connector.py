from contextlib import contextmanager

from nebula3.Config import Config
from nebula3.gclient.net import ConnectionPool
from pydantic import BaseModel


class ConnectorConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str


class Connector:
    def __init__(self, config: ConnectorConfig):
        self.connector_config = config
        self.connection_pool = ConnectionPool()
        self.is_connected = False
        self.config = Config()
        self.config.max_connection_pool_size = 10

    def connect(self) -> bool:
        try:
            self.is_connected = self.connection_pool.init([(self.connector_config.host, self.connector_config.port)], self.config)  # Pass config with timeout
            return self.is_connected
        except Exception:
            return False

    @contextmanager
    def session(self, name_space: str | None = None):
        if not self.is_connected:
            if not self.connect():
                raise ConnectionError("Cannot establish connection to Nebula Graph")
        session = None
        try:
            session = self.connection_pool.get_session(self.connector_config.username, self.connector_config.password)
            if name_space:
                result = session.execute(f"USE {name_space}")
                if not result.is_succeeded():
                    raise Exception(f"Failed to use namespace {name_space}: {result.error_msg()}")
            yield session
        finally:
            if session:
                session.release()
