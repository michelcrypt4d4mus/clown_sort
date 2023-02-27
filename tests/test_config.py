from tests.conftest import PROCESSED_DIR, SORTED_DIR


def test_config_folders(test_config):
    assert SORTED_DIR.is_dir()
    assert PROCESSED_DIR.is_dir()
