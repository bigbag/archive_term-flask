# -*- coding: utf-8 -*-
"""
    Модель для счетов

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from web import app, db

from helpers import date_helper

from models.base_model import BaseModel
from models.firm import Firm

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER


class PaymentAccount(db.Model, BaseModel):

    __bind_key__ = 'payment'
    __tablename__ = 'account'

    STATUS_GENERATED = 0
    STATUS_PAID = 3

    id = db.Column(db.Integer, primary_key=True)
    firm_id = db.Column(db.Integer, nullable=False, index=True)
    generated_date = db.Column(db.DateTime, nullable=False, index=True)
    summ = db.Column(db.Integer, nullable=False)
    items_count = db.Column(db.Integer)
    status = db.Column(db.Integer, nullable=False, index=True)
    filename = db.Column(db.String(128))

    def __init__(self):
        self.generated_date = date_helper.get_current_date()
        self.status = self.STATUS_GENERATED

    def select_list(self, firm_id, **kwargs):
        date_pattern = '%d.%m.%Y'

        order = kwargs['order'] if 'order' in kwargs else 'generated_date desc'
        limit = kwargs['limit'] if 'limit' in kwargs else 10
        page = kwargs['page'] if 'page' in kwargs else 1

        query = PaymentAccount.query.filter(
            PaymentAccount.firm_id == firm_id)
        query = query.order_by(order)
        account_list = query.paginate(page, limit, False).items

        result = []
        for account in account_list:
            data = dict(
                id=account.id,
                generated_date=date_helper.from_utc(
                    account.generated_date,
                    app.config['TZ']).strftime(date_pattern),
                summ=float(account.summ) / 100,
                items_count=account.items_count,
                status=account.status
            )
            result.append(data)

        value = dict(
            result=result,
            count=query.count(),
        )

        return value

    @staticmethod
    def get_filename(firm_id, search_date):
        return "account_firm_%s_date_%s.pdf" % (
            firm_id,
            search_date.strftime('%m_%Y'))

    def generate_pdf(self):
        if not self.firm_id or not self.summ:
            return False

        firm = Firm.query.get(self.firm_id)
        if not firm:
            return False

        pdfmetrics.registerFont(TTFont('PDFFont', app.config['PDF_FONT']))
        styles = getSampleStyleSheet()
        data = [str(self.firm_id), str(self.summ), str(self.generated_date)]
        data = '&'.join(data)

        doc = SimpleDocTemplate(
            "%s/%s" % (app.config['PDF_FOLDER'], self.filename), pagesize=A4)

        style = styles['Normal']
        style.fontName = "PDFFont"
        style.alignment = TA_LEFT

        story = []
        style.fontSize = 12
        story.append(Paragraph(u'ООО «МОБИСПОТ РУС»',
                               style))

        style.fontSize = 11
        story.append(Paragraph(u'140180, г.Москва ул.Сельскохозяйственная, д.11, корп. 3',
                               style))

        story.append(Spacer(1, 0.8 * inch))
        story.append(Paragraph(u'Получатель: ООО «МОБИСПОТ РУС»',
                               style))
        story.append(Paragraph(u'ИНН 7717770408 КПП 771701001',
                               style))
        story.append(Paragraph(u'Расчетный счет №40702.810.1.00000000914',
                               style))

        story.append(Spacer(1, 0.4 * inch))

        style.fontSize = 10
        story.append(Paragraph(u'Банк получателя: РАСЧЕТНАЯ НЕБАНКОВСКАЯ КРЕДИТНАЯ ОРГАНИЗАЦИЯ «РИБ»',
                               style))
        style.fontSize = 11
        story.append(Paragraph(u'БИК 44583793',
                               style))
        story.append(Paragraph(u'Корр. счет 30103.810.6.00000000793',
                               style))

        story.append(Spacer(1, 0.8 * inch))

        style_header = styles['Heading1']
        style_header.fontName = "PDFFont"
        style_header.fontSize = 16
        style_header.alignment = TA_CENTER

        date_pattern = '%d.%m.%Y'
        date_pdf = date_helper.from_utc(
            self.generated_date,
            app.config['TZ']).strftime(date_pattern)
        if self.id:
            story.append(Paragraph(u'Счет №%s от %s' % (self.id, date_pdf),
                                   style_header))
        else:
            story.append(Paragraph(u'Счет от %s' % date_pdf,
                                   style_header))

        if firm.legal_entity:
            story.append(Paragraph(u'Плательщик: %s' % firm.legal_entity,
                                   style))
            story.append(Spacer(1, 0.1 * inch))

        data_count = 1
        item_price = PaymentAccount.format_summ(self.summ)
        if self.items_count and firm.transaction_comission:
            data_count = str(self.items_count)
            price = int(round(float(self.summ) / self.items_count))
            item_price = PaymentAccount.format_summ(price)

        data_summ = PaymentAccount.format_summ(self.summ)

        data = [
            [u'№', u'Наименование', u'Количество, шт.',
                u'Цена, руб.', u'Сумма, руб.'],
            ['1', u'Информационная\n услуга по учету',
                data_count, item_price, data_summ],
            ['', '', '', u'НДС не\n облагается', '-'],
            ['', '', '', 'Всего к оплате:', data_summ]]

        t = Table(data, colWidths=1.21 * inch)
        table_style = TableStyle(
            [('BACKGROUND', (0, 0), (4, 0), colors.Color(0.7, 0.7, 0.7))])
        table_style.add('GRID', (0, 0), (4, 0), 1, colors.Color(0.7, 0.7, 0.7))
        table_style.add('FONTNAME', (0, 0), (4, 3), "PDFFont")
        table_style.add('FONTSIZE', (1, 1), (1, 1), 9)
        table_style.add('GRID', (0, 1), (4, 3), 1, colors.gray)
        table_style.add('ALIGN', (0, 0), (4, 3), 'LEFT')
        table_style.add('VALIGN', (0, 0), (4, 3), 'TOP')

        t.setStyle(table_style)
        story.append(t)

        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph(u'НДС и налогом с продаж не облагается, согласно НК РФ глава 26.2, статья 346.11, п.2 "Упрощенная система налогообложения"',
                               style))

        if ('PDF_GENERAL_MANAGER' in app.config):
            story.append(Spacer(1, 0.3 * inch))
            sign = Image(app.config['PDF_GENERAL_MANAGER_SIGN'], width=65, height=52)
            data = [
                [u'  Генеральный директор', sign, u'(%s)   ' % app.config['PDF_GENERAL_MANAGER']]]
            table_manager = Table(data, colWidths=2.1 * inch)
            table_style = TableStyle([('FONTNAME', (0, 0), (2, 0), "PDFFont")])
            table_style.add('VALIGN', (0, 0), (2, 0), 'MIDDLE')
            table_style.add('ALIGN', (0, 0), (0, 0), 'LEFT')
            table_style.add('ALIGN', (1, 0), (1, 0), 'CENTER')
            table_style.add('ALIGN', (2, 0), (2, 0), 'RIGHT')
            table_manager.setStyle(table_style)
            story.append(table_manager)
            story.append(Spacer(1, 0.2 * inch))
        else:
            story.append(Spacer(1, 0.7 * inch))
            story.append(Paragraph(u'Генеральный директор',
                                   style))
            story.append(Spacer(1, 0.6 * inch))

        if ('PDF_CHIEF_ACCOUNTANT' in app.config):
            sign = Image(app.config['PDF_CHIEF_ACCOUNTANT_SIGN'], width=65, height=52)

            data = [
                [u'  Главный бухгалтер', sign, u'(%s)   ' % app.config['PDF_CHIEF_ACCOUNTANT']]]
            table_manager = Table(data, colWidths=2.1 * inch)
            table_style = TableStyle([('FONTNAME', (0, 0), (2, 0), "PDFFont")])
            table_style.add('VALIGN', (0, 0), (2, 0), 'MIDDLE')
            table_style.add('ALIGN', (0, 0), (0, 0), 'LEFT')
            table_style.add('ALIGN', (1, 0), (1, 0), 'CENTER')
            table_style.add('ALIGN', (2, 0), (2, 0), 'RIGHT')
            table_manager.setStyle(table_style)
            story.append(table_manager)
        else:
            story.append(Paragraph(u'Главный бухгалтер',
                                   style))

        if ('PDF_STAMP' in app.config):
            stamp = Image(app.config['PDF_STAMP'], width=110, height=110)
            stamp.hAlign = 'LEFT'
            story.append(stamp)

        doc.build(story)

        return True

    @staticmethod
    def format_summ(summ):
        summ = int(round(summ))
        return "%02d-%02d" % (summ / 100, summ % 100)

    def get_month_year(self):
        months = date_helper.get_locale_months()
        return '%s %s' % (months[self.generated_date.month - 2],
                          self.generated_date.year)
