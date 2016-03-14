import datetime
from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateView, StateAction, Button
from trytond.transaction import Transaction
from trytond.pyson import PYSONEncoder, Date
from trytond.pool import Pool

__all__ = ['LotsByLocationStart', 'LotsByLocation']


class LotsByLocationStart(ModelView):
    'Lots by Location'
    __name__ = 'stock.lots_by_location.start'
    forecast_date = fields.Date(
        'At Date', help=('Allow to compute expected '
            'stock quantities for this date.\n'
            '* An empty value is an infinite date in the future.\n'
            '* A date in the past will provide historical values.'))

    @staticmethod
    def default_forecast_date():
        Date_ = Pool().get('ir.date')
        return Date_.today()


class LotsByLocation(Wizard):
    'Lots by Location'
    __name__ = 'stock.lots_by_location'
    start = StateView('stock.lots_by_location.start',
        'stock_lot_quantity.lots_by_location_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open', 'tryton-ok', True),
            ])
    open = StateAction('stock_lot_quantity.act_lots_by_location')

    def do_open(self, action):
        pool = Pool()
        Location = pool.get('stock.location')
        Lang = pool.get('ir.lang')

        context = {}
        context['locations'] = Transaction().context.get('active_ids')
        date = self.start.forecast_date or datetime.date.max
        context['stock_date_end'] = Date(date.year, date.month, date.day)
        action['pyson_context'] = PYSONEncoder().encode(context)

        locations = Location.browse(context['locations'])

        for code in [Transaction().language, 'en_US']:
            langs = Lang.search([
                    ('code', '=', code),
                    ])
            if langs:
                break
        lang = langs[0]
        date = Lang.strftime(date, lang.code, lang.date)

        action['name'] += ' - (%s) @ %s' % (
            ','.join(l.name for l in locations), date)
        return action, {}
