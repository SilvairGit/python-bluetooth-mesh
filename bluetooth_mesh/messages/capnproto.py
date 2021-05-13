import tempfile

import capnp

from bluetooth_mesh.messages.capnproto_generator import generate


def load_definitions():
    print("Loading CapNProto messages definitions")

    with tempfile.NamedTemporaryFile(
        suffix=".capnp", mode="w+", encoding="utf-8"
    ) as tmp_file:
        generate(0x97EBBC55406EDFB4, file=tmp_file)
        tmp_file.seek(0)
        source = tmp_file.read()

        capnp.remove_import_hook()
        messages = capnp.load(tmp_file.name)

        return source, messages


SOURCE, MESSAGES = load_definitions()

AccessMessage = MESSAGES.AccessMessage
