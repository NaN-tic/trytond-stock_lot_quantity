# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval, If
from trytond.transaction import Transaction

__all__ = ['Lot', 'Move']


class Lot(metaclass=PoolMeta):
    __name__ = 'stock.lot'

    def _get_warehouses():
        pool = Pool()
        User = pool.get('res.user')
        Config = pool.get('stock.configuration')
        Location = pool.get('stock.location')
        user = User(Transaction().user)
        config = Config(1)
        warehouses = None
        if user.warehouse:
            warehouses = [user.warehouse]
        elif config.warehouse:
            warehouses = [config.warehouse]
        else:
            warehouses = Location.search(['type', '=', 'warehouse'])

        return warehouses

    @classmethod
    def get_quantity(cls, lots, name):
        "Return null instead of 0.0 if no locations in context"
        if not Transaction().context.get('locations'):
            warehouses = cls._get_warehouses()

            if not warehouses:
                return {}.fromkeys([l.id for l in lots], None)

            locations = [w.storage_location.id for w in warehouses]
            Transaction().set_context(locations=locations)

        return super(Lot, cls).get_quantity(lots, name)

    @classmethod
    def search_quantity(cls, name, domain=None):
        if not Transaction().context.get('locations'):
            warehouses = cls._get_warehouses()
            if warehouses:
                locations = [w.storage_location.id for w in warehouses]
                Transaction().set_context(locations=locations)
        return super().search_quantity(name, domain)


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
