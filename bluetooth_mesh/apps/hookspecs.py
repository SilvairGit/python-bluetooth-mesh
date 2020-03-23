import pluggy

hookspec = pluggy.HookspecMarker("bluetooth_mesh")


@hookspec
def application_mixins():
    pass
