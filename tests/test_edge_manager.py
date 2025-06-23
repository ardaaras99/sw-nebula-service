from datetime import datetime

import pytest

from sw_nebula_service.managers.edge_manager import EdgeManager
from sw_nebula_service.managers.edge_type_manager import EdgeTypeManager
from sw_nebula_service.managers.space_manager import SpaceManager
from sw_nebula_service.managers.tag_manager import TagManager
from sw_nebula_service.managers.vertex_manager import VertexManager
from tests.utils import PersonNode, TestNode


class TestRelation:
    pass


@pytest.fixture
def setup_namespace_with_edges(connector):
    """Set up a test namespace with tags, vertices, and edge types for edge manager tests."""
    space_manager = SpaceManager(connector=connector)
    space_manager.create_namespace(name_space="test_edge_manager", partition_num=100, replica_factor=1, vid_type="INT64")

    # Wait for the space to be created
    import time

    time.sleep(5)  # Wait for space to be created

    # Create tags
    tag_manager = TagManager(connector=connector)
    tag_manager.create_tag(name_space="test_edge_manager", node_class=TestNode)
    tag_manager.create_tag(name_space="test_edge_manager", node_class=PersonNode)

    # Wait for tags to be created
    time.sleep(5)  # Wait for tags to be created

    # Create vertices
    vertex_manager = VertexManager(connector=connector)

    # Create test nodes
    test_node = TestNode(field_1="test_value", field_3=123, field_5=123.45, field_7=True, field_9=datetime.now())

    person_node = PersonNode(name="Test Person", age=30, gender="male", email="test@example.com", phone="1234567890", address="123 Test St")

    # Insert vertices
    vertex_manager.insert_vertex(name_space="test_edge_manager", node=test_node, vid=1)
    vertex_manager.insert_vertex(name_space="test_edge_manager", node=person_node, vid=2)

    # Create edge type
    edge_type_manager = EdgeTypeManager(connector=connector)
    edge_type_manager.create_edge_type_without_property(name_space="test_edge_manager", edge_class=TestRelation)

    # Wait for edge type to be created
    time.sleep(5)  # Wait for edge type to be created

    return "test_edge_manager"


def test_edge_manager_init(connector):
    """Test that the edge manager can be initialized."""
    edge_manager = EdgeManager(connector=connector)
    assert edge_manager.connector == connector


def test_insert_edge_without_property(connector, setup_namespace_with_edges):
    """Test that the edge manager can insert an edge without properties."""
    edge_manager = EdgeManager(connector=connector)

    try:
        result = edge_manager.insert_edge_without_property(name_space=setup_namespace_with_edges, edge_type="test_relation", src_vid=1, dst_vid=2)
        assert result
    except Exception as e:
        pytest.fail(f"Failed to insert edge without property: {e}")
