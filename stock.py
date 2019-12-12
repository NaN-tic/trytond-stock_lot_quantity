# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction

__all__ = ['Lot', 'Move']


class Lot(metaclass=PoolMeta):
    __name__ = 'stock.lot'

    @classmethod
    def get_quantity(cls, lots, name):
        "Return null instead of 0.0 if no locations in context"
        if not Transaction().context.get('locations'):
            return {}.fromkeys([l.id for l in lots], None)
        return super(Lot, cls).get_quantity(lots, name)


class Move(metaclass=PoolMeta):
    __name__ = 'stock.move'

    @classmethod
    def __setup__(cls):
        super(Move, cls).__setup__()
        cls.lot.context['locations'] = If(Eval('from_location'), [Eval('from_location')], [])
        if 'from_location' not in cls.lot.depends:
            cls.lot.depends.append('from_location')
        cls.lot.loading = 'lazy'

        if 'product' not in cls.lot.depends:
            cls.lot.depends.append('product')
        cls.lot.states['readonly'] |= ~Eval('product') | ~Eval('from_location')
