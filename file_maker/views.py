import os
from django.http import HttpResponse,FileResponse
from django.shortcuts import render, redirect
from reportlab.pdfbase import pdfmetrics   # 注册字体
from reportlab.pdfbase.ttfonts import TTFont # 字体类
from reportlab.platypus import Table, SimpleDocTemplate, Paragraph, Image  # 报告内容相关类
from reportlab.lib.pagesizes import letter, landscape  # 页面的标志尺寸(8.5*inch, 11*inch)
from reportlab.lib.styles import getSampleStyleSheet  # 文本样式
from reportlab.lib import colors  # 颜色模块
from reportlab.graphics.charts.barcharts import VerticalBarChart  # 图表类
from reportlab.graphics.charts.legends import Legend  # 图例类
from reportlab.graphics.shapes import Drawing  # 绘图工具
from reportlab.lib.units import cm  # 单位：cm

from mol_registration.models import mol_props, cutome_fields_data
from django.forms.models import model_to_dict
import pubchempy as pcp, requests, random
# 注册字体(提前准备好字体文件, 如果同一个文件需要多种字体可以注册多个)
pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttf'))
pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
def compound_report(request):
    compound_id = request.GET.get('compound_report_for')
    item = cutome_fields_data.objects.get(compound_id=compound_id)
    item_dict = model_to_dict(item, exclude=['id', 'compound', 'batch_id'])
    item_primary = item.compound
    item_primary_dict = model_to_dict(item_primary,
                                      exclude=['mol_file', 'mol_file_path', 'smiles', 'img_file', 'fingerprint'])
    smiles = item.compound.smiles
    cid = pcp.get_compounds(smiles, "smiles")[0].cid
    if cid:
        compound = pcp.Compound.from_cid(cid)
        compound_iupac = compound.iupac_name
        url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/%s/JSON/?heading=CAS" % cid
        user_agent = [
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        ]
        response = requests.get(url, headers={'User-Agent': random.choice(user_agent), "connection": "close"},
                                timeout=5,
                                verify=False)
        if response:
            casnum = response.json()['Record']['Section'][0]['Section'][0]['Section'][0]["Information"][0]['Value'][
                'StringWithMarkup'][0]['String']
        else:
            casnum = 'None'
    else:
        compound_iupac = 'No retrieved name'
        casnum = 'None'

    data = [('Property', 'Value')]
    data.append(('IUPAC Name',compound_iupac))
    for key, value in item_primary_dict.items():
        data.append((key.capitalize().replace('_',' '), value))

    for key, value in item_dict.items():
        data.append((key.capitalize().replace('_',' '), value))

    content = list()
    # 添加标题
    content.append(Graphs.draw_title('Compound Report:%s' % compound_id))
    # 添加图片
    content.append(Graphs.draw_img('./register/template/static/mol_image/%s.png' % compound_id))
    # 添加段落文字
    content.append(Graphs.draw_text(''))
    # 添加小标题
    content.append(Graphs.draw_title(''))
    content.append(Graphs.draw_little_title(''))
    # 添加表格
    content.append(Graphs.draw_table(*data))

    # # 生成图表
    # content.append(Graphs.draw_title(''))
    # content.append(Graphs.draw_little_title('热门城市的就业情况'))
    # b_data = [(25400, 12900, 20100, 20300, 20300, 17400), (15800, 9700, 12982, 9283, 13900, 7623)]
    # ax_data = ['BeiJing', 'ChengDu', 'ShenZhen', 'ShangHai', 'HangZhou', 'NanJing']
    # leg_items = [(colors.red, '平均薪资'), (colors.green, '招聘量')]
    # content.append(Graphs.draw_bar(b_data, ax_data, leg_items))

    # 生成pdf文件
    doc = SimpleDocTemplate('./register/template/static/compound_report/%s.pdf' % compound_id, pagesize=letter)
    doc.build(content)
    file_path = './register/template/static/compound_report/%s.pdf' % compound_id
    pdf = open(file_path,'rb')
    response = FileResponse(pdf)
    # 'application/pdf'表示返回的文件格式是pdf，根据需要替换
    response['Content-Type'] = 'application/pdf'
    response['Content-Disposition'] = 'attachment; filename=Compound Report {0}.pdf'.format(compound_id)
    return response




class Graphs:
    # 绘制标题
    @staticmethod
    def draw_title(title: str):
        # 获取所有样式表
        style = getSampleStyleSheet()
        # 拿到标题样式
        ct = style['Heading2']
        # 单独设置样式相关属性
        ct.fontName = 'Vera'  # 字体名
        ct.fontSize = 16  # 字体大小
        ct.leading = 20  # 行间距
        ct.textColor = colors.black  # 字体颜色
        ct.alignment = 1  # 居中
        ct.bold = True
        # 创建标题对应的段落，并且返回
        return Paragraph(title, ct)

    # 绘制小标题
    @staticmethod
    def draw_little_title(title: str):
        # 获取所有样式表
        style = getSampleStyleSheet()
        # 拿到标题样式
        ct = style['Normal']
        # 单独设置样式相关属性
        ct.fontName = 'SimSun'  # 字体名
        ct.fontSize = 15  # 字体大小
        ct.leading = 30  # 行间距
        ct.textColor = colors.red  # 字体颜色
        # 创建标题对应的段落，并且返回
        return Paragraph(title, ct)

    # 绘制普通段落内容
    @staticmethod
    def draw_text(text: str):
        # 获取所有样式表
        style = getSampleStyleSheet()
        # 获取普通样式
        ct = style['Normal']
        ct.fontName = 'SimSun'
        ct.fontSize = 12
        ct.wordWrap = 'CJK'  # 设置自动换行
        ct.alignment = 0  # 左对齐
        ct.firstLineIndent = 32  # 第一行开头空格
        ct.leading = 25
        return Paragraph(text, ct)

    # 绘制表格
    @staticmethod
    def draw_table(*args):
        # 列宽度
        col_width = 200
        style = [
            ('FONTNAME', (0, 0), (-1, -1), 'Vera'),  # 字体
            ('FONTSIZE', (0, 0), (-1, 0), 12),  # 第一行的字体大小
            ('FONTSIZE', (0, 1), (-1, -1), 10),  # 第二行到最后一行的字体大小
            ('BACKGROUND', (0, 0), (-1, 0), '#cccccc'),  # 设置第一行背景颜色
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # 第一行水平居中
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),  # 第二行到最后一行左右左对齐
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # 所有表格上下居中对齐
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkslategray),  # 设置表格内文字颜色
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # 设置表格框线为grey色，线宽为0.5
            # ('SPAN', (0, 1), (0, 2)),  # 合并第一列二三行
            # ('SPAN', (0, 3), (0, 4)),  # 合并第一列三四行
            # ('SPAN', (0, 5), (0, 6)),  # 合并第一列五六行
            # ('SPAN', (0, 7), (0, 8)),  # 合并第一列五六行
        ]
        table = Table(args, colWidths=col_width, style=style)
        return table

    # 创建图表
    @staticmethod
    def draw_bar(bar_data: list, ax: list, items: list):
        drawing = Drawing(500, 250)
        bc = VerticalBarChart()
        bc.x = 45  # 整个图表的x坐标
        bc.y = 45  # 整个图表的y坐标
        bc.height = 200  # 图表的高度
        bc.width = 350  # 图表的宽度
        bc.data = bar_data
        bc.strokeColor = colors.black  # 顶部和右边轴线的颜色
        bc.valueAxis.valueMin = 5000  # 设置y坐标的最小值
        bc.valueAxis.valueMax = 26000  # 设置y坐标的最大值
        bc.valueAxis.valueStep = 2000  # 设置y坐标的步长
        bc.categoryAxis.labels.dx = 2
        bc.categoryAxis.labels.dy = -8
        bc.categoryAxis.labels.angle = 20
        bc.categoryAxis.categoryNames = ax

        # 图示
        leg = Legend()
        leg.fontName = 'SimSun'
        leg.alignment = 'right'
        leg.boxAnchor = 'ne'
        leg.x = 475  # 图例的x坐标
        leg.y = 240
        leg.dxTextSpace = 10
        leg.columnMaximum = 3
        leg.colorNamePairs = items
        drawing.add(leg)
        drawing.add(bc)
        return drawing

    # 绘制图片
    @staticmethod
    def draw_img(path):
        img = Image(path)  # 读取指定路径下的图片
        img.drawWidth = 6 * cm  # 设置图片的宽度
        img.drawHeight = 6 * cm  # 设置图片的高度
        # img.hAlign = 0
        return img



