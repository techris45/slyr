#!/usr/bin/env python
"""
MultiLayerSymbol and subclasses

COMPLETE INTERPRETATION
"""

from slyr_community.parser.stream import Stream
from slyr_community.parser.object import Object
from slyr_community.parser.objects.symbol_layer import SymbolLayer


class MultiLayerSymbol(Object):
    """
    Base class for multi-layer symbols
    """

    def __init__(self):
        super().__init__()
        self.layers = []
        self.symbol_level = 0

    def children(self):
        res = super().children()
        for l in self.layers:
            if l:
                res.append(l)
        return res

    def to_dict(self):
        out = {
            'levels': [],
            'symbol_level': self.symbol_level
        }
        for l in self.layers:
            out['levels'].append(l.to_dict())
        return out


class MultiLayerLineSymbol(MultiLayerSymbol):
    """
    Multi-layer Line symbol
    """

    @staticmethod
    def cls_id():
        return '7914e5fa-c892-11d0-8bb6-080009ee4e41'

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream: Stream, version):
        self.symbol_level = SymbolLayer.read_symbol_level(stream)

        number_layers = stream.read_uint('layer count')
        for i in range(number_layers):
            layer = stream.read_object('symbol layer {}/{}'.format(i + 1, number_layers))
            self.layers.extend([layer])

        for l in self.layers:
            l.read_enabled(stream)
        for l in self.layers:
            l.read_locked(stream)

        if version >= 2:
            for l in self.layers:
                l.read_tags(stream)


class MultiLayerFillSymbol(MultiLayerSymbol):
    """
    Multi-layer fill symbol
    """

    @staticmethod
    def cls_id():
        return '7914e604-c892-11d0-8bb6-080009ee4e41'

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream: Stream, version):
        self.symbol_level = SymbolLayer.read_symbol_level(stream)

        _ = stream.read_object('unused color')

        number_layers = stream.read_int('layers')
        for i in range(number_layers):
            layer = stream.read_object('symbol layer {}/{}'.format(i + 1, number_layers))
            self.layers.extend([layer])

        for l in self.layers:
            l.read_enabled(stream)
        for l in self.layers:
            l.read_locked(stream)

        if version >= 2:
            for l in self.layers:
                l.read_tags(stream)


class MultiLayerMarkerSymbol(MultiLayerSymbol):
    """
    Multi-layer marker symbol.
    """

    @staticmethod
    def cls_id():
        return '7914e5ff-c892-11d0-8bb6-080009ee4e41'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.halo = False
        self.halo_size = 0
        self.halo_symbol = None

    @staticmethod
    def compatible_versions():
        return [1, 2, 3]

    def to_dict(self):
        out = super().to_dict()
        out['halo'] = self.halo
        out['halo_size'] = self.halo_size
        out['halo_symbol'] = self.halo_symbol.to_dict() if self.halo_symbol is not None else None
        return out

    def children(self):
        res = super().children()
        if self.halo_symbol:
            res.append(self.halo_symbol)
        return res

    def read(self, stream: Stream, version):
        self.symbol_level = SymbolLayer.read_symbol_level(stream)

        # consume unused properties - MultiLayerMarkerSymbol implements IMarkerSymbol
        # so that the size/offsets/angle are required properties. But they aren't used
        # or exposed anywhere for MultiLayerMarkerSymbol
        _ = stream.read_double('unused marker size')
        _ = stream.read_double('unused marker x/y/offset or angle')
        _ = stream.read_double('unused marker x/y/offset or angle')
        _ = stream.read_double('unused marker x/y/offset or angle')
        _ = stream.read_object('unused color')

        self.halo = stream.read_int() == 1
        self.halo_size = stream.read_double('halo size')

        self.halo_symbol = stream.read_object('halo')

        # useful stuff
        number_layers = stream.read_int('layers')
        for i in range(number_layers):
            layer = stream.read_object('symbol layer {}/{}'.format(i + 1, number_layers))
            self.layers.extend([layer])

        for l in self.layers:
            l.read_enabled(stream)
        for l in self.layers:
            l.read_locked(stream)

        if version > 1:
            _ = stream.read_double('unknown size')
            _ = stream.read_double('unknown size')

        if version >= 3:
            for l in self.layers:
                l.read_tags(stream)
