# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
import time

from odoo import fields, models, tools, SUPERUSER_ID, _

from odoo.tools.safe_eval import safe_eval, time
from odoo.tools.misc import find_in_path, ustr
from odoo.tools import config, is_html_empty, parse_version

from collections import OrderedDict
import re
import pyidaungsu as pds

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'

    font = fields.Selection(selection_add=[('pyidaungsu', 'Pyidaungsu')])

class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf(self, res_ids=None, data=None):
        """
        :rtype: bytes
        """
        if not data:
            data = {}
        data.setdefault('report_type', 'pdf')

        # access the report details with sudo() but evaluation context as sudo(False)
        self_sudo = self.sudo()

        # In case of test environment without enough workers to perform calls to wkhtmltopdf,
        # fallback to render_html.
        if (tools.config['test_enable'] or tools.config['test_file']) and not self.env.context.get('force_report_rendering'):
            return self_sudo._render_qweb_html(res_ids, data=data)

        # As the assets are generated during the same transaction as the rendering of the
        # templates calling them, there is a scenario where the assets are unreachable: when
        # you make a request to read the assets while the transaction creating them is not done.
        # Indeed, when you make an asset request, the controller has to read the `ir.attachment`
        # table.
        # This scenario happens when you want to print a PDF report for the first time, as the
        # assets are not in cache and must be generated. To workaround this issue, we manually
        # commit the writes in the `ir.attachment` table. It is done thanks to a key in the context.
        context = dict(self.env.context)
        if not config['test_enable'] and 'commit_assetsbundle' not in context:
            context['commit_assetsbundle'] = True

        # Disable the debug mode in the PDF rendering in order to not split the assets bundle
        # into separated files to load. This is done because of an issue in wkhtmltopdf
        # failing to load the CSS/Javascript resources in time.
        # Without this, the header/footer of the reports randomly disappear
        # because the resources files are not loaded in time.
        # https://github.com/wkhtmltopdf/wkhtmltopdf/issues/2083
        context['debug'] = False

        save_in_attachment = OrderedDict()
        # Maps the streams in `save_in_attachment` back to the records they came from
        stream_record = dict()
        if res_ids:
            # Dispatch the records by ones having an attachment and ones requesting a call to
            # wkhtmltopdf.
            Model = self.env[self_sudo.model]
            record_ids = Model.browse(res_ids)
            wk_record_ids = Model
            if self_sudo.attachment:
                for record_id in record_ids:
                    attachment = self_sudo.retrieve_attachment(record_id)
                    if attachment:
                        stream = self_sudo._retrieve_stream_from_attachment(
                            attachment)
                        save_in_attachment[record_id.id] = stream
                        stream_record[stream] = record_id
                    if not self_sudo.attachment_use or not attachment:
                        wk_record_ids += record_id
            else:
                wk_record_ids = record_ids
            res_ids = wk_record_ids.ids

        # A call to wkhtmltopdf is mandatory in 2 cases:
        # - The report is not linked to a record.
        # - The report is not fully present in attachments.
        if save_in_attachment and not res_ids:
            _logger.info('The PDF report has been generated from attachments.')
            if len(save_in_attachment) > 1:
                self._raise_on_unreadable_pdfs(
                    save_in_attachment.values(), stream_record)
            return self_sudo._post_pdf(save_in_attachment), 'pdf'

        if self.get_wkhtmltopdf_state() == 'install':
            # wkhtmltopdf is not installed
            # the call should be catched before (cf /report/check_wkhtmltopdf) but
            # if get_pdf is called manually (email template), the check could be
            # bypassed
            raise UserError(
                _("Unable to find Wkhtmltopdf on this system. The PDF can not be created."))

        html = self_sudo.with_context(
            context)._render_qweb_html(res_ids, data=data)[0]
        '''
        Unicode Correction for Myanmar Font
        '''
        html_string = html.decode('utf-8')
        new_word = detect_myanmar_font(html_string)
        html = new_word.encode('utf-8')

        bodies, html_ids, header, footer, specific_paperformat_args = self_sudo.with_context(
            context)._prepare_html(html)

        if self_sudo.attachment and set(res_ids) != set(html_ids):
            raise UserError(_("The report's template '%s' is wrong, please contact your administrator. \n\n"
                              "Can not separate file to save as attachment because the report's template does not contains the attributes 'data-oe-model' and 'data-oe-id' on the div with 'article' classname.") % self.name)

        pdf_content = self._run_wkhtmltopdf(
            bodies,
            header=header,
            footer=footer,
            landscape=context.get('landscape'),
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=context.get('set_viewport_size'),
        )
        if res_ids:
            self._raise_on_unreadable_pdfs(
                save_in_attachment.values(), stream_record)
            _logger.info('The PDF report has been generated for model: %s, records %s.' % (
                self_sudo.model, str(res_ids)))
            return self_sudo._post_pdf(save_in_attachment, pdf_content=pdf_content, res_ids=html_ids), 'pdf'
        return pdf_content, 'pdf'


def detect_myanmar_font(text):
    new_text = ''
    # Define a regular expression pattern for Myanmar script
    myanmar_pattern = re.compile(r'[\u1000-\u109F]+', re.UNICODE)

    # Find all matches in the text
    matches = myanmar_pattern.finditer(text)

    # Extract start and end indices for each match
    result = [(match.start(), match.end()) for match in matches]
    count = 0
    past_index = 0
    for res in result:
        reindex_val = dynamic_reindex(text[res[0]:res[1]])
        text = text.replace(text[res[0]:res[1]],reindex_val)
    return text


def dynamic_reindex(input_string):
    vals = pds.tokenize(input_string)
    input_val = []
    for val in vals:
        if '\u103C' in val and '\u1031' in val:
            input_val.append(
                '\u1031' + (' \u103C' + val.replace('\u103C', '')).replace('\u1031', ''))
            # input_val.append(' \u103C' + val.replace('\u103C', ''))
            # input_val.append('\u1031' + val.replace('\u1031', ''))
        elif '\u103C' in val:
            input_val.append(' \u103C' + val.replace('\u103C', ''))
        elif '\u1031' in val:
            if len(val) >= 4 and '\u1038' not in val or len(val) == 3 and '\u103D' in val:
                input_val.append('\u1031' + val.replace('\u1031', ''))
            elif len(val) >=4 and '\u1038' in val:
                input_val.append(' \u1031' + val.replace('\u1031', ''))
            else:
                input_val.append(val)
        else:
            input_val.append(val)
    input_string = ''.join(input_val)
    return input_string
