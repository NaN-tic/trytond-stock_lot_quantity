# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import stock
from . import location


def register():
    Pool.register(
        stock.Lot,
        stock.Move,
        location.LotsByLocationStart,
        module='stock_lot_quantity', type_='model')
    Pool.register(
        location.LotsByLocation,
        module='stock_lot_quantity', type_='wizard')
