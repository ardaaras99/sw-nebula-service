import pytest

from sw_nebula_service.managers.connector import Connector, ConnectorConfig


def test_connector_init():
    """Test that the connector can be initialized."""
    config = ConnectorConfig(host="192.168.3.70", port=32113, username="root", password="nebula")
    connector = Connector(config)
    assert connector.connector_config == config
    assert not connector.is_connected


def test_connector_connect():
    """Test that the connector can connect to Nebula Graph."""
    config = ConnectorConfig(host="192.168.3.70", port=32113, username="root", password="nebula")  # noqa: S106
    connector = Connector(config)
    connected = connector.connect()
    assert connected
    assert connector.is_connected


def test_connector_session():
    """Test that the connector can create a session."""
    config = ConnectorConfig(host="192.168.3.70", port=32113, username="root", password="nebula")  # noqa: S106
    connector = Connector(config)
    with connector.session() as session:
        assert session is not None


def test_connector_session_with_namespace(connector):
    """Test that the connector can create a session with a namespace."""
    # First create a namespace to use
    with connector.session() as session:
        result = session.execute("CREATE SPACE IF NOT EXISTS test_connector_session (partition_num=100, replica_factor=1, vid_type=INT64)")
        assert result.is_succeeded()

    # Wait for the space to be created
    import time

    time.sleep(5)  # Wait for space to be created

    # Now test using the namespace
    try:
        with connector.session("test_connector_session") as session:
            assert session is not None
    except Exception as e:
        pytest.fail(f"Failed to create session with namespace: {e}")


def test_connector_session_invalid_namespace():
    """Test that the connector raises an exception for an invalid namespace."""
    config = ConnectorConfig(host="192.168.3.70", port=32113, username="root", password="nebula")  # noqa: S106
    connector = Connector(config)
    with pytest.raises(Exception):
        with connector.session("invalid_namespace") as session:
            pass
