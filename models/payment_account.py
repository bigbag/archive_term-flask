# -*- coding: utf-8 -*-
"""
    Модель для счетов

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
import os
import copy
from web import app, db

from helpers import date_helper

from models.base_model import BaseModel
from models.firm import Firm

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT


class PaymentAccount(db.Model, BaseModel):

    __bind_key__ = 'payment'
    __tablename__ = 'account'

    STATUS_GENERATED = 0
    STATUS_PAID = 1

    id = db.Column(db.Integer, primary_key=True)
    firm_id = db.Column(db.Integer, nullable=False, index=True)
    generated_date = db.Column(db.DateTime, nullable=False, index=True)
    summ = db.Column(db.Integer, nullable=False)
    items_count = db.Column(db.Integer)
    status = db.Column(db.Integer, nullable=False, index=True)
    filename = db.Column(db.String(128))
    item_price = db.Column(db.Integer)
    gprs_terms_count = db.Column(db.Integer)

    def __init__(self):
        self.generated_date = date_helper.get_current_date()
        self.status = self.STATUS_GENERATED

    def delete(self):
        if self.filename and os.path.isfile("%s/%s" % (app.config['PDF_FOLDER'], self.filename)):
            os.remove("%s/%s" % (app.config['PDF_FOLDER'], self.filename))
        db.session.delete(self)
        db.session.commit()

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

    @staticmethod
    def get_act_filename(firm_id, search_date):
        return "act_firm_%s_date_%s.pdf" % (
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
        story.append(Paragraph(u'Расчетный счет №40702810100000000914',
                               style))

        story.append(Spacer(1, 0.4 * inch))

        style.fontSize = 10
        story.append(Paragraph(u'Банк получателя: РАСЧЕТНАЯ НЕБАНКОВСКАЯ КРЕДИТНАЯ ОРГАНИЗАЦИЯ «РИБ»',
                               style))
        style.fontSize = 11
        story.append(Paragraph(u'БИК 044583793',
                               style))
        story.append(Paragraph(u'Корр. счет 30103810600000000793',
                               style))

        story.append(Spacer(1, 0.5 * inch))

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

        data_price = self.format_summ(self.item_price)
        data_rows = 3

        price_header = u'Цена, руб.'
        if firm.transaction_percent:
            price_header = u'Цена, %'
            data_price = str(float(firm.transaction_percent) / 100) + '%'

        data = [
            [u'№', u'Наименование', u'Количество, шт.', price_header, u'Сумма, руб.']]

        if self.gprs_terms_count and firm.gprs_rate:
            data_rows += 1
            gprs_summ = self.gprs_terms_count * firm.gprs_rate
            gprs_price = self.format_summ(firm.gprs_rate)
            data_summ = self.format_summ(self.summ - gprs_summ)
            data_gprs_summ = self.format_summ(gprs_summ)

            data.append(['1', u'Информационная\n услуга по учету', str(
                self.items_count), data_price, data_summ])
            data.append(['2', u'Услуга\n GPRS связи', str(
                self.gprs_terms_count), gprs_price, data_gprs_summ])
        else:
            data_summ = self.format_summ(self.summ)
            data.append(['1', u'Информационная\n услуга по учету', str(
                self.items_count), data_price, data_summ])

        data.append(['', '', '', u'НДС не\n облагается', '-'])
        data.append(
            ['', '', '', 'Всего к оплате:', self.format_summ(self.summ)])

        t = Table(data, colWidths=1.21 * inch)
        table_style = TableStyle(
            [('BACKGROUND', (0, 0), (4, 0), colors.Color(0.7, 0.7, 0.7))])
        table_style.add('GRID', (0, 0), (4, 0), 1, colors.Color(0.7, 0.7, 0.7))
        table_style.add('FONTNAME', (0, 0), (4, data_rows), "PDFFont")
        table_style.add('FONTSIZE', (1, 1), (1, 1), 9)
        table_style.add('GRID', (0, 1), (4, data_rows), 1, colors.gray)
        table_style.add('ALIGN', (0, 0), (4, data_rows), 'LEFT')
        table_style.add('VALIGN', (0, 0), (4, data_rows), 'TOP')

        t.setStyle(table_style)
        story.append(t)

        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph(u'НДС и налогом с продаж не облагается, согласно НК РФ глава 26.2, статья 346.11, п.2 "Упрощенная система налогообложения"',
                               style))

        if ('PDF_GENERAL_MANAGER' in app.config):
            story.append(Spacer(1, 0.3 * inch))
            sign = Image(
                app.config['PDF_GENERAL_MANAGER_SIGN'], width=65, height=52)
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
            sign = Image(
                app.config['PDF_CHIEF_ACCOUNTANT_SIGN'], width=65, height=52)

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
    def firm_has_account(id):
        if PaymentAccount.query.filter_by(firm_id=id).count():
            return True
        return False

    @staticmethod
    def format_summ(summ):
        summ = int(round(summ))
        return "%02d-%02d" % (summ / 100, summ % 100)

    @staticmethod
    def summ_comma(summ):
        summ = int(round(summ))
        return "%02d,%02d" % (summ / 100, summ % 100)

    @staticmethod
    def get_underline():
        styles = getSampleStyleSheet()
        style = styles['Normal']
        style.fontName = "PDFFont"
        style.alignment = TA_CENTER
        style.fontSize = 2

        line = Paragraph(
            u'<u>_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________<u>', style)

        return line

    def get_month_year(self):
        months = date_helper.get_locale_months()
        return '%s %s' % (months[self.generated_date.month - 2],
                          self.generated_date.year)

    def generate_act(self):
        if not self.firm_id or not self.summ or not self.generated_date:
            return False

        firm = Firm.query.get(self.firm_id)
        if not firm:
            return False

        story = []
        fontSize = 9
        pdfmetrics.registerFont(TTFont('PDFFont', app.config['PDF_FONT']))
        styles = getSampleStyleSheet()
        data = [str(self.firm_id), str(self.summ), str(self.generated_date)]
        data = '&'.join(data)

        doc = SimpleDocTemplate(
            "%s/%s" % (app.config['PDF_FOLDER'], self.get_act_filename(firm.id, self.generated_date)), pagesize=A4)

        style = styles['Normal']
        style.fontName = "PDFFont"
        style.fontSize = fontSize
        style.alignment = TA_CENTER

        story.append(Spacer(1, 0.3 * inch))

        months_in_genitive = date_helper.get_locale_months_in_genitive()
        story.append(Paragraph(u'Акт № <font color="gray">MBS-%07d</font> от <font color="gray">%02d %s %s</font>' %
                               (self.id, self.generated_date.day, months_in_genitive[self.generated_date.month], self.generated_date.year), style))

        story.append(self.get_underline())

        linestyle = copy.copy(style)

        linestyle.alignment = TA_LEFT
        linestyle.leftIndent = 10
        linestyle.spaceBefore = 18

        story.append(Paragraph(
            u'Исполнитель:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ООО "МОБИСПОТ РУС"', linestyle))

        story.append(Spacer(1, 0.2 * inch))

        if firm.legal_entity:
            story.append(Paragraph(
                u'Заказчик:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<font color="gray">%s</font>' % firm.legal_entity, linestyle))

        story.append(Spacer(1, 0.3 * inch))

        months = date_helper.get_locale_months()
        linestyle = copy.copy(style)
        linestyle.alignment = TA_CENTER
        product = Paragraph(u'Информационно-технололгические услуги за <font color="gray">%s %s</font>' %
                            (months[self.generated_date.month - 1], self.generated_date.year), linestyle)

        linestyle = copy.copy(style)
        linestyle.alignment = TA_RIGHT
        summ = Paragraph(u'<font color="gray">%s</font>' %
                         self.summ_comma(self.summ), linestyle)

        data = [
            [u'№', u'Товар', u'Кол-во', u'Ед.', u'Цена', u'Сумма'],
            [u'1', product, u'1', u'шт.', summ, summ]]

        t = Table(data, rowHeights=[0.6 * inch, 0.4 * inch], colWidths=[
                  0.4 * inch, None, 0.6 * inch, 0.4 * inch, 0.9 * inch, 0.9 * inch])

        table_style = TableStyle()
        table_style.add('INNERGRID', (0, 0), (5, 1), 0.5, colors.black)
        table_style.add('BOX', (0, 0), (5, 1), 1, colors.black)
        table_style.add('FONTNAME', (0, 0), (5, 1), "PDFFont")
        table_style.add('FONTSIZE', (0, 0), (5, 1), fontSize)
        table_style.add('FONTCOLOR', (4, 1), (5, 1), colors.gray)
        table_style.add('ALIGN', (0, 0), (5, 0), 'CENTER')
        table_style.add('ALIGN', (0, 1), (1, 1), 'CENTER')
        table_style.add('ALIGN', (2, 1), (2, 1), 'RIGHT')
        table_style.add('ALIGN', (3, 1), (3, 1), 'CENTER')
        table_style.add('ALIGN', (4, 1), (5, 1), 'RIGHT')
        table_style.add('VALIGN', (0, 0), (5, 0), 'MIDDLE')
        table_style.add('VALIGN', (0, 1), (5, 1), 'TOP')

        t.setStyle(table_style)
        story.append(t)

        story.append(Spacer(1, 0.2 * inch))

        data = [
            ['', u'Итого:', summ],
            ['', u'В том числе НДС', '']]

        t = Table(data, colWidths=[4.1 * inch, 1.2 * inch, 0.8 * inch])
        table_style = TableStyle([('FONTNAME', (0, 0), (2, 1), "PDFFont")])
        table_style.add('ALIGN', (0, 0), (2, 1), 'RIGHT')
        table_style.add('FONTSIZE', (0, 0), (2, 1), fontSize)
        t.setStyle(table_style)
        story.append(t)

        story.append(Spacer(1, 0.3 * inch))

        linestyle = copy.copy(style)
        story.append(Paragraph(u'Всего оказано услуг 1, на сумму <font color="gray">%s руб.</font>' %
                               self.summ_comma(self.summ), linestyle))
        story.append(Paragraph(
            u'НДС и налогом с продаж не облагается, согласно НК РФ глава 26.2, статья 346.11, ', linestyle))
        story.append(
            Paragraph(u'п.2 "Упрощенная система налогообложения"', linestyle))

        story.append(Spacer(1, 0.6 * inch))

        linestyle = copy.copy(linestyle)
        linestyle.leftIndent = 10
        linestyle.rightIndent = 10
        story.append(Paragraph(
            u'Вышеперечисленные услуги выполнены полностью и в срок. Заказчик претензий по объему, качеству и срокам оказания услуг не имеет.', linestyle))

        story.append(Spacer(1, 0.3 * inch))
        story.append(self.get_underline())

        stamp = Image(
            './static/account_data/img/stamp_and_sign.jpg', width=137, height=160)
        img_underline = Image(
            './static/account_data/img/underline.jpg', width=137, height=35)

        data = [
            [u'Исполнитель', stamp, u'Заказчик', img_underline]]

        t = Table(data)

        table_style = TableStyle()
        table_style.add('FONTNAME', (0, 0), (3, 0), "PDFFont")
        table_style.add('FONTSIZE', (0, 0), (3, 0), fontSize)
        table_style.add('VALIGN', (0, 0), (3, 0), 'TOP')
        table_style.add('TOPPADDING', (0, 0), (0, 0), 25)
        table_style.add('RIGHTPADDING', (0, 0), (0, 0), 0)
        table_style.add('TOPPADDING', (2, 0), (2, 0), 25)
        table_style.add('RIGHTPADDING', (2, 0), (2, 0), 0)

        t.setStyle(table_style)
        story.append(t)

        doc.build(story)

        return True
