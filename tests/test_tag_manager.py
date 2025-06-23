import pytest

from sw_nebula_service.managers.space_manager import SpaceManager
from sw_nebula_service.managers.tag_manager import TagManager, convert_fields_of_class_to_nebula_types
from tests.utils import PersonNode, TestNode


@pytest.fixture
def setup_namespace(connector):
    """Set up a test namespace for tag manager tests."""
    space_manager = SpaceManager(connector=connector)
    space_manager.create_namespace(name_space="test_tag_manager", partition_num=100, replica_factor=1, vid_type="INT64")

    # Wait for the space to be created
    import time

    time.sleep(5)  # Wait for space to be created

    return "test_tag_manager"


def test_tag_manager_init(connector):
    """Test that the tag manager can be initialized."""
    tag_manager = TagManager(connector=connector)
    assert tag_manager.connector == connector


def test_convert_fields_of_class_to_nebula_types():
    """Test that fields can be converted to Nebula types."""
    fields = convert_fields_of_class_to_nebula_types(TestNode)
    assert len(fields) == 10
    assert "field_1 string" in fields
    assert "field_3 int" in fields
    assert "field_5 float" in fields
    assert "field_7 bool" in fields
    assert "field_9 datetime" in fields


def test_create_tag(connector, setup_namespace):
    """Test that the tag manager can create a tag."""
    tag_manager = TagManager(connector=connector)
    try:
        tag_manager.create_tag(name_space=setup_namespace, node_class=TestNode)
    except Exception as e:
        pytest.fail(f"Failed to create tag: {e}")


def test_create_tag_index(connector, setup_namespace):
    """Test that the tag manager can create a tag index."""
    tag_manager = TagManager(connector=connector)

    tag_manager.create_tag(name_space=setup_namespace, node_class=TestNode)

    import time

    time.sleep(5)

    try:
        result = tag_manager.create_tag_index(name_space=setup_namespace, tag_name="test_node", index_name="test_node_index")
        assert result
    except Exception as e:
        pytest.fail(f"Failed to create tag index: {e}")


def test_create_index_on_tag_property(connector, setup_namespace):
    """Test that the tag manager can create an index on a tag property."""
    tag_manager = TagManager(connector=connector)

    # First create a tag
    tag_manager.create_tag(name_space=setup_namespace, node_class=PersonNode)

    # Wait for the tag to be created
    import time

    time.sleep(5)  # Wait for tag to be created

    # Now create an index on a property
    try:
        result = tag_manager.create_index_on_tag_property(name_space=setup_namespace, tag_name="person_node", index_name="person_name_index", property_name="name")
        assert result
    except Exception as e:
        pytest.fail(f"Failed to create index on tag property: {e}")
