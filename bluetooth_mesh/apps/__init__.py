import pluggy

from bluetooth_mesh.apps import hookspecs

hookimpl = pluggy.HookimplMarker("bluetooth_mesh")


def get_plugin_manager():
    plugin_manager = pluggy.PluginManager("bluetooth_mesh")
    plugin_manager.add_hookspecs(hookspecs)
    plugin_manager.load_setuptools_entrypoints("bluetooth_mesh")
    return plugin_manager
