import pytest
from pydantic import BaseModel

from sw_nebula_service.managers.edge_type_manager import EdgeTypeManager
from sw_nebula_service.managers.space_manager import SpaceManager
from sw_nebula_service.models import BaseNebulaRelation


class TestNode(BaseModel):
    name: str
    age: int


class TestRelation(BaseNebulaRelation):
    source_node: TestNode
    target_node: TestNode


class SimpleRelation:
    pass


@pytest.fixture
def setup_namespace(connector):
    """Set up a test namespace for edge type manager tests."""
    space_manager = SpaceManager(connector=connector)
    space_manager.create_namespace(name_space="test_edge_type_manager", partition_num=100, replica_factor=1, vid_type="INT64")

    # Wait for the space to be created
    import time

    time.sleep(5)  # Wait for space to be created

    return "test_edge_type_manager"


def test_edge_type_manager_init(connector):
    """Test that the edge type manager can be initialized."""
    edge_type_manager = EdgeTypeManager(connector=connector)
    assert edge_type_manager.connector == connector


def test_create_edge_type_without_property(connector, setup_namespace):
    """Test that the edge type manager can create an edge type without properties."""
    edge_type_manager = EdgeTypeManager(connector=connector)

    try:
        result = edge_type_manager.create_edge_type_without_property(name_space=setup_namespace, edge_class=SimpleRelation)
        assert result
    except Exception as e:
        pytest.fail(f"Failed to create edge type without property: {e}")


def test_create_edge_type_with_property(connector, setup_namespace):
    """Test that the edge type manager can create an edge type with properties."""
    edge_type_manager = EdgeTypeManager(connector=connector)

    try:
        result = edge_type_manager.create_edge_type_with_property(name_space=setup_namespace, edge_class=TestRelation)
        assert result
    except Exception as e:
        pytest.fail(f"Failed to create edge type with property: {e}")


def test_create_edge_type_index(connector, setup_namespace):
    """Test that the edge type manager can create an edge type index."""
    edge_type_manager = EdgeTypeManager(connector=connector)

    # First create an edge type
    edge_type_manager.create_edge_type_without_property(name_space=setup_namespace, edge_class=SimpleRelation)

    # Wait for the edge type to be created
    import time

    time.sleep(5)  # Wait for edge type to be created

    # Now create an index
    try:
        result = edge_type_manager.create_edge_type_index(name_space=setup_namespace, edge_type="simple_relation", index_name="simple_relation_index")
        assert result
    except Exception as e:
        pytest.fail(f"Failed to create edge type index: {e}")
