from typing import Any, Callable, List, Tuple

from construct import (
    Adapter,
    Array,
    BitsInteger,
    Bytes,
    BytesInteger,
    Computed,
    Const,
    Default,
    Embedded,
    Enum,
    FixedSized,
    Flag,
    FormatField,
    GreedyBytes,
    GreedyRange,
    NullStripped,
    Padded,
    Pass,
    Rebuild,
    Renamed,
    Restreamed,
    Select,
    StringEncoded,
    Struct,
    Switch,
    Transformed,
)
from docutils import nodes
from sphinx.ext.autodoc import DataDocumenter, members_option
from sphinx.util import logging

logger = logging.getLogger(__name__)


def level_option(arg):
    return int(arg)


class Skip:
    pass


class ConstructDocumenter(DataDocumenter):
    """
    Specialized Documenter subclass for construct items.
    """
    objtype = 'construct'
    directivetype = 'data'

    option_spec = dict(DataDocumenter.option_spec)
    option_spec["level"] = level_option

    INDENT = ' ' * 4

    def document_struct(self, subcon, level):
        doc = []

        for field in subcon.subcons:
            annotation, subdoc = self.document_subcon(field, level + 1)

            if annotation is not Skip:
                annotation = ': %s' % annotation if annotation else ''
                name = '`%s`' % field.name if field.name else ''
                if name and annotation:
                    doc.append('%s* %s%s' % (self.INDENT * level, name, annotation))

            doc += subdoc

        return ':py:class:`Struct` of', doc

    def document_switch(self, subcon, level):
        doc = []
        for name, field in subcon.cases.items():
            _, subdoc = self.document_subcon(field, level + 1)

            doc.append('%s* :py:data:`%s`' % (self.INDENT * level, name))
            doc += subdoc

        return ':py:class:`Switch` by `%s`' % subcon.keyfunc.__getfield__(), doc

    def document_enum(self, subcon, level):
        annotation, subdoc = self.document_subcon(subcon.subcon, level + 1)
        return ':py:class:`Enum` of :py:class:`%s` as %s' % (subcon.ENUM.__name__, annotation), subdoc

    def document_const(self, subcon):
        return ':py:class:`Const` :py:data:`%s`' % subcon.value, []

    def document_select(self, subcon, level):
        doc = []

        for field in subcon.subcons:
            annotation, subdoc = self.document_subcon(field, level + 1)

            if annotation is not Skip:
                annotation = ': %s' % annotation if field.name and annotation else annotation
                name = ':py:class:`%s`' % field.name if field.name else ''
                if name or annotation:
                    doc.append('%s* %s%s' % (self.INDENT * level, name, annotation))

            doc += subdoc

        return ':py:class:`Select` from', doc

    def document_array(self, subcon, level):
        annotation, subdoc = self.document_subcon(subcon.subcon, level + 1)
        if isinstance(subcon.count, Callable):
            return ':py:class:`Array[%s]` of %s' % (subcon.count.__getfield__(), annotation), subdoc
        else:
            return ':py:class:`Array[%i]` of %s' % (subcon.count, annotation), subdoc

    def document_format_field(self, subcon):
        DOC = {
            "B": "Uint8",
            "H": "Uint16",
            "L": "Uint32",
            "Q": "Uint64",
            "b": "Int8",
            "h": "Int16",
            "l": "Int32",
            "q": "Int64",
        }

        return ':py:class:`%s`' % DOC[subcon.fmtstr[1]], []

    def document_bytes_integer(self, subcon):
        return ':py:class:`{}nt{}`'.format('I' if subcon.signed else 'Ui', subcon.length * 8), []

    def document_bits_integer(self, subcon):
        return ':py:class:`{}nt{}`'.format('I' if subcon.signed else 'Ui', subcon.length), []

    def document_bytes(self, subcon):
        return ':py:class:`bytes[%i]`' % subcon.length, []

    def document_range(self, subcon, level):
        annotation, subdoc = self.document_subcon(subcon.subcon, level + 1)
        return ':py:class:`Range` of %s' % annotation, subdoc

    def document_subcon(self, subcon, level=0):
        if self.options.level is not None and level > self.options.level:
            return '', []

        if hasattr(subcon, '__construct_doc__'):
            return self.document_subcon(subcon.__construct_doc__, level)

        if isinstance(subcon, Enum):
            return self.document_enum(subcon, level)

        if isinstance(subcon, (Renamed, Adapter, Default, Transformed,
                               Restreamed, Rebuild, FixedSized,
                               NullStripped)):
            return self.document_subcon(subcon.subcon, level)

        if isinstance(subcon, Embedded):
            annotation, subdoc = self.document_subcon(subcon.subcon, level - 1)
            return Skip, subdoc

        if isinstance(subcon, Struct):
            return self.document_struct(subcon, level)

        if isinstance(subcon, Switch):
            return self.document_switch(subcon, level)

        if isinstance(subcon, Select):
            return self.document_select(subcon, level)

        if isinstance(subcon, Array):
            return self.document_array(subcon, level)

        if isinstance(subcon, GreedyRange):
            return self.document_range(subcon, level)

        if isinstance(subcon, FormatField):
            return self.document_format_field(subcon)

        if isinstance(subcon, BytesInteger):
            return self.document_bytes_integer(subcon)

        if isinstance(subcon, BitsInteger):
            return self.document_bits_integer(subcon)

        if isinstance(subcon, Bytes):
            return self.document_bytes(subcon)

        if isinstance(subcon, Padded) and not subcon.name:
            return Skip, []

        if isinstance(subcon, Computed):
            return Skip, []

        if isinstance(subcon, Const):
            return self.document_const(subcon)

        if isinstance(subcon, StringEncoded):
            return ':py:class:`str`', []

        if subcon is Pass:
            return ':py:data:`None`', []

        if subcon is Flag:
            return ':py:class:`bool`', []

        if subcon is GreedyBytes:
            return ':py:class:`bytes`', []

        logger.warn('Uknown subconstruct: %s %s', subcon.name, subcon)

        return ': :py:class:`UNKNOWN`', []

    def get_doc(self, encoding: str = None, ignore: int = 1) -> List[List[str]]:
        _, subdoc = self.document_subcon(self.object)
        return [subdoc]


def setup(app):
    app.add_autodocumenter(ConstructDocumenter)

    return {'version': '0.1', 'parallel_read_safe': True}
