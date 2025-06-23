import pytest

from sw_nebula_service.managers.connector import Connector, ConnectorConfig


@pytest.fixture
def connector():
    """Return a connector instance for testing."""
    config = ConnectorConfig(host="192.168.3.70", port=32113, username="root", password="nebula")  # noqa: S106
    connector = Connector(config)
    return connector


@pytest.fixture
def namespace():
    """Return a test namespace name."""
    return "test_namespace"


#! NameSpace, Tag ve EdgeType ları burada oluşturmak mantıklı olabilir, yoksa error veriryor
