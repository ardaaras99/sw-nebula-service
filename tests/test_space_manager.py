import pytest

from sw_nebula_service.managers.space_manager import SpaceManager


def test_space_manager_init(connector):
    """Test that the space manager can be initialized."""
    space_manager = SpaceManager(connector=connector)
    assert space_manager.connector == connector


def test_create_namespace(connector):
    """Test that the space manager can create a namespace."""
    space_manager = SpaceManager(connector=connector)
    try:
        result = space_manager.create_namespace(name_space="test_space_manager", partition_num=100, replica_factor=1, vid_type="INT64")
        assert result
    except Exception as e:
        pytest.fail(f"Failed to create namespace: {e}")


def test_create_namespace_with_custom_params(connector):
    """Test that the space manager can create a namespace with custom parameters."""
    space_manager = SpaceManager(connector=connector)
    try:
        result = space_manager.create_namespace(name_space="test_space_manager_custom", partition_num=50, replica_factor=1, vid_type="INT64")
        assert result
    except Exception as e:
        pytest.fail(f"Failed to create namespace with custom parameters: {e}")


def test_delete_all_namespaces(connector):
    """Test that the space manager can delete all namespaces."""
    space_manager = SpaceManager(connector=connector)

    # First create a test namespace
    space_manager.create_namespace(name_space="test_space_manager_delete")

    # Wait for the space to be created
    import time

    time.sleep(5)  # Wait for space to be created

    # Now delete all namespaces
    try:
        space_manager.delete_all_namespaces()

        # Verify spaces are deleted by trying to use one
        with pytest.raises(Exception):
            with connector.session("test_space_manager_delete") as session:
                pass
    except Exception as e:
        pytest.fail(f"Failed to delete all namespaces: {e}")
