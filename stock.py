# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval, If
from trytond.transaction import Transaction


class Lot(metaclass=PoolMeta):
    __name__ = 'stock.lot'

    @classmethod
    def get_quantity(cls, lots, name):
        "Return null instead of 0.0 if no locations in context"
        pool = Pool()
        User = pool.get('res.user')
        Location = pool.get('stock.location')
        if not Transaction().context.get('locations'):
            user = User(Transaction().user)
            warehouses = None
            if user.warehouse:
                warehouses = [user.warehouse]
            else:
                warehouses = Location.search(['type', '=', 'warehouse'])
            if not warehouses:
                return {}.fromkeys([l.id for l in lots], None)

            locations = [w.storage_location.id for w in warehouses]
            Transaction().set_context(locations=locations)
        return super(Lot, cls).get_quantity(lots, name)


class Move(metaclass=PoolMeta):
    __name__ = 'stock.move'

    @classmethod
    def __setup__(cls):
        super(Move, cls).__setup__()
        cls.lot.context['locations'] = If(Eval('from_location'),
            [Eval('from_location')], [])
        if 'from_location' not in cls.lot.depends:
            cls.lot.depends.append('from_location')
        cls.lot.loading = 'lazy'

        if 'product' not in cls.lot.depends:
            cls.lot.depends.append('product')
        cls.lot.states['readonly'] |= ~Eval('product') | ~Eval('from_location')
