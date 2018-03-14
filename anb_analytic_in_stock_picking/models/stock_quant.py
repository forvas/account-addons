# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from odoo import models, fields, _
from odoo.exceptions import UserError
from collections import defaultdict
import logging
_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _create_account_move_line(self, move, credit_account_id,
                                  debit_account_id, journal_id):
        # group quants by cost
        quant_cost_qty = defaultdict(lambda: 0.0)
        for quant in self:
            quant_cost_qty[quant.cost] += quant.qty
        AccountMove = self.env['account.move']
        for cost, qty in quant_cost_qty.iteritems():
            move_lines = move._prepare_account_move_line(
                qty, cost, credit_account_id, debit_account_id)
            if move_lines:
                date = self._context.get('force_period_date',
                                         fields.Date.context_today(self))
                new_account_move = AccountMove.create({
                    'journal_id': journal_id,
                    'line_ids': move_lines,
                    'date': date,
                    'ref': move.picking_id.name,
                    'picking': move.picking_id.id})
                new_account_move.post()
