# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .stock import *
from .location import *


def register():
    Pool.register(
        Lot,
        Move,
        LotsByLocationStart,
        module='stock_lot_quantity', type_='model')
    Pool.register(
        LotsByLocation,
        module='stock_lot_quantity', type_='wizard')
