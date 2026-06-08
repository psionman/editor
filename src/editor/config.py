"""Config for Editor launcher."""

from psiconfig import TomlConfig

from editor.constants import CONFIG_PATH, USER_DATA_DIR

DEFAULT_CONFIG = {
    'data_directory': USER_DATA_DIR,
    'my_int': 1,
    'my_bool': True,
    'geometry': {
        'frm_main': '500x600',
        'frm_config': '700x300',
    },
}


def read_config(restore_defaults: bool = False) -> TomlConfig:
    """Return the config file."""
    return TomlConfig(
        path=CONFIG_PATH,
        defaults=DEFAULT_CONFIG,
        restore_defaults=restore_defaults)


def save_config(updated_config: TomlConfig) -> TomlConfig | None:
    """Save the config file."""
    # pylint: disable=no-member)
    result = updated_config.save()
    if result != updated_config.STATUS_OK:
        return None
    return TomlConfig(CONFIG_PATH)


config = read_config()
