from bluetooth_mesh.apps import hookimpl


class LocalNetworkMixin:
    async def get_network(self, *args, **kwargs):
        # TODO: add a way to use a local provisioning database

        raise NotImplementedError(
            "Cannot obtain network database without Silvair commissioning API"
        )


@hookimpl(trylast=True)
def application_mixins():
    return (LocalNetworkMixin,)
