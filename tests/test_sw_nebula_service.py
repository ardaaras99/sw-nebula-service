import sw_nebula_service


def test_import() -> None:
    """Test that the package can be imported without errors."""
    assert isinstance(sw_nebula_service.__name__, str)
