"""
LifeBeyond · 数字彼岸  商业计划书 Word 文档构建脚本
基于 306 份实证调研、技术接受模型(TAM)、SEM 路径分析与 K-means 用户聚类
输出: /workspace/projects/public/LifeBeyond_Business_Plan.docx
风格: 蓝色科技风 / 学术商业语言 / 数据驱动
"""

import os
import io
import math
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ------------------------------------------------------------
# 全局配置
# ------------------------------------------------------------
OUTPUT_DIR = '/workspace/projects/public'
ASSET_DIR  = '/tmp/bp_assets'
OUTFILE    = os.path.join(OUTPUT_DIR, 'LifeBeyond_Business_Plan.docx')

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ASSET_DIR, exist_ok=True)

# 蓝色科技风配色 (hex 字符串, 不含 #)
COLOR = {
    'primary':  '0B2A5B',
    'accent':   '1E88E5',
    'neon':     '00E5FF',
    'ink':      '1A1F36',
    'muted':    '5A6B89',
    'stroke':   'C8D7E8',
    'panel':    'F0F6FF',
    'warn':     'F4A11A',
    'danger':   'E0395E',
    'success':  '1FAE6F',
}

def RGB(h):
    return RGBColor.from_string(h)

# Matplotlib 主题
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'Source Han Sans CN', 'WenQuanYi Zen Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ------------------------------------------------------------
# 工具函数
# ------------------------------------------------------------
def set_cell_bg(cell, hex_color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), hex_color)
    tc_pr.append(shd)

def set_cell_border(cell, color='C8D7E8', size='6'):
    tc_pr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for edge in ('top', 'left', 'bottom', 'right'):
        b = OxmlElement(f'w:{edge}')
        b.set(qn('w:val'), 'single')
        b.set(qn('w:sz'), size)
        b.set(qn('w:color'), color)
        tcBorders.append(b)
    tc_pr.append(tcBorders)

def add_para(doc, text, *, size=10.5, bold=False, color='1A1F36',
             align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent_first=True,
             space_before=0, space_after=4, line_spacing=1.5):
    p = doc.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    if indent_first:
        pf.first_line_indent = Cm(0.74)
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line_spacing
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGB(color)
    run.font.name = 'Times New Roman'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')
    return p

def add_heading(doc, text, level=1):
    """学术商业风格的章节标题"""
    sizes = {0: 22, 1: 17, 2: 14, 3: 12}
    colors = {0: COLOR['primary'], 1: COLOR['primary'], 2: COLOR['accent'], 3: COLOR['ink']}
    bolds = {0: True, 1: True, 2: True, 3: True}
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = p.paragraph_format
    pf.space_before = Pt(16 if level <= 1 else 10)
    pf.space_after = Pt(6)
    pf.line_spacing = 1.2
    run = p.add_run(text)
    run.font.size = Pt(sizes.get(level, 11))
    run.font.bold = bolds.get(level, True)
    run.font.color.rgb = RGB(colors.get(level, COLOR['ink']))
    run.font.name = 'Times New Roman'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')
    if level == 1:
        # 给标题加底部蓝色细线
        p_pr = p._p.get_or_add_pPr()
        pbdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '8')
        bottom.set(qn('w:space'), '4')
        bottom.set(qn('w:color'), COLOR['accent'])
        pbdr.append(bottom)
        p_pr.append(pbdr)
    return p

def add_callout(doc, label, body, color_key='accent'):
    """蓝色卡片式重点提示框"""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_bg(cell, COLOR['panel'])
    set_cell_border(cell, color=COLOR[color_key], size='12')
    cell.width = Cm(16)
    p1 = cell.paragraphs[0]
    p1.paragraph_format.space_after = Pt(2)
    r1 = p1.add_run(f'  ▍{label}  ')
    r1.font.size = Pt(10.5)
    r1.font.bold = True
    r1.font.color.rgb = RGB(COLOR[color_key])
    r1.font.name = '思源黑体 CN'
    r1._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')
    p2 = cell.add_paragraph()
    p2.paragraph_format.space_before = Pt(2)
    p2.paragraph_format.space_after = Pt(4)
    p2.paragraph_format.line_spacing = 1.5
    r2 = p2.add_run(f'    {body}')
    r2.font.size = Pt(10)
    r2.font.color.rgb = RGB(COLOR['ink'])
    r2.font.name = 'Times New Roman'
    r2._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')
    doc.add_paragraph()  # 间距

def add_bullet(doc, text, level=0, bold_lead=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(0.74 + level * 0.74)
    pf.space_before = Pt(0)
    pf.space_after = Pt(3)
    pf.line_spacing = 1.45
    bullet_char = '■ ' if level == 0 else ('▸ ' if level == 1 else '· ')
    r0 = p.add_run(bullet_char)
    r0.font.size = Pt(10)
    r0.font.color.rgb = RGB(COLOR['accent'])
    r0.font.name = 'Times New Roman'
    if bold_lead:
        rL = p.add_run(bold_lead + '  ')
        rL.font.size = Pt(10.5)
        rL.font.bold = True
        rL.font.color.rgb = RGB(COLOR['primary'])
        rL.font.name = 'Times New Roman'
        rL._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')
    r1 = p.add_run(text)
    r1.font.size = Pt(10.5)
    r1.font.color.rgb = RGB(COLOR['ink'])
    r1.font.name = 'Times New Roman'
    r1._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')

def add_table(doc, headers, rows, col_widths=None):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    # 表头
    for i, h in enumerate(headers):
        c = t.cell(0, i)
        set_cell_bg(c, COLOR['primary'])
        set_cell_border(c, COLOR['primary'], '8')
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(h)
        r.font.size = Pt(10)
        r.font.bold = True
        r.font.color.rgb = RGB('FFFFFF')
        r.font.name = 'Times New Roman'
        r._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')
        if col_widths:
            c.width = Cm(col_widths[i])
    # 数据行
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            c = t.cell(1 + ri, ci)
            set_cell_bg(c, 'FFFFFF' if ri % 2 == 0 else COLOR['panel'])
            set_cell_border(c, COLOR['stroke'], '4')
            c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(str(val))
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGB(COLOR['ink'])
            r.font.name = 'Times New Roman'
            r._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')
            if col_widths:
                c.width = Cm(col_widths[ci])

def add_image(doc, path, width_cm=14.5, caption=None):
    doc.add_picture(path, width=Cm(width_cm))
    last = doc.paragraphs[-1]
    last.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if caption:
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.space_before = Pt(0)
        cp.paragraph_format.space_after = Pt(8)
        r = cp.add_run(caption)
        r.font.size = Pt(9)
        r.font.italic = True
        r.font.color.rgb = RGB(COLOR['muted'])
        r.font.name = 'Times New Roman'
        r._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')

def page_break(doc):
    doc.add_page_break()

# ------------------------------------------------------------
# 图表生成
# ------------------------------------------------------------
def chart_market_size():
    """中国虚拟数字人市场规模 (艾瑞数据 2023 vs 2025e)"""
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=160)
    years = ['2023', '2024E', '2025E']
    pull = [3334.7, 4720.5, 6402.7]
    core = [205.2, 320.4, 480.6]
    x = np.arange(len(years))
    w = 0.36
    b1 = ax.bar(x - w/2, pull, w, label='带动产业规模', color='#1E88E5', edgecolor='#0B2A5B')
    b2 = ax.bar(x + w/2, core, w, label='核心市场规模', color='#00E5FF', edgecolor='#0B2A5B')
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width()/2, b.get_height() + 80,
                    f'{b.get_height():.1f}', ha='center', fontsize=9, color='#0B2A5B')
    ax.set_ylabel('市场规模(亿元)', fontsize=10, color='#0B2A5B')
    ax.set_title('中国虚拟数字人市场规模演进  数据来源：艾瑞咨询', fontsize=11, color='#0B2A5B', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.legend(loc='upper left', frameon=False)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    p = os.path.join(ASSET_DIR, 'market_size.png')
    fig.savefig(p, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return p

def chart_user_radar():
    """三类聚类用户六维雷达"""
    dims = ['AI 技术\n接受态度', '产品\n使用意愿', '功能吸引力\n偏好', '伦理顾虑\n程度', '付费\n接受度', '商业化\n反感度']
    rational    = [4.32, 4.02, 4.25, 2.89, 3.86, 2.65]
    emotional   = [4.15, 4.47, 4.38, 3.27, 3.52, 3.78]
    ethical     = [2.08, 1.86, 1.93, 4.51, 1.24, 4.62]
    angles = np.linspace(0, 2*np.pi, len(dims), endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(8, 6), dpi=160, subplot_kw=dict(polar=True))
    for vals, label, col in [
        (rational, '理性接受型', '#1E88E5'),
        (emotional, '情感依赖型', '#E0395E'),
        (ethical, '伦理顾虑型', '#F4A11A'),
    ]:
        v = vals + vals[:1]
        ax.plot(angles, v, label=label, color=col, linewidth=2)
        ax.fill(angles, v, color=col, alpha=0.15)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dims, fontsize=9, color='#0B2A5B')
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1','2','3','4','5'], color='#5A6B89', fontsize=8)
    ax.grid(color='#C8D7E8', linestyle='--', alpha=0.6)
    ax.set_title('三类用户群体核心特征量化对比 (5 分制)', fontsize=11, color='#0B2A5B', pad=18)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False, fontsize=9)
    p = os.path.join(ASSET_DIR, 'user_radar.png')
    fig.savefig(p, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return p

def chart_acceptance_donut():
    """整体接受度甜甜圈"""
    labels = ['完全接受 18.6%', '有条件接受 32.4%', '中立观望 18.6%', '部分反对 13.7%', '明确拒绝 16.7%']
    vals = [18.6, 32.4, 18.6, 13.7, 16.7]
    cols = ['#1FAE6F', '#1E88E5', '#5A6B89', '#F4A11A', '#E0395E']
    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=160)
    wedges, _ = ax.pie(vals, colors=cols, startangle=90, wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2))
    ax.text(0, 0.15, 'N = 306', ha='center', fontsize=12, color='#0B2A5B', weight='bold')
    ax.text(0, -0.1, '有效样本', ha='center', fontsize=9, color='#5A6B89')
    ax.text(0, -0.35, '总拒绝率 30.4%', ha='center', fontsize=9, color='#E0395E', weight='bold')
    ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=False, fontsize=9)
    ax.set_title('公众对 AI 数字复生技术整体接受度分布', fontsize=11, color='#0B2A5B', pad=10)
    p = os.path.join(ASSET_DIR, 'acceptance_donut.png')
    fig.savefig(p, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return p

def chart_sem_path():
    """SEM 路径系数横向条形图"""
    paths = ['H4 功能吸引力 → 使用意愿', 'H3 开放性态度 → 使用意愿',
             'H1 付费偏好 → 使用意愿', 'H2 伦理顾虑 → 使用意愿']
    coefs = [0.452, 0.318, 0.276, 0.187]
    pvals = ['p<0.001', 'p<0.001', 'p<0.01', 'p<0.05']
    fig, ax = plt.subplots(figsize=(8, 3.6), dpi=160)
    bars = ax.barh(paths, coefs, color=['#1E88E5', '#00E5FF', '#1FAE6F', '#F4A11A'], edgecolor='#0B2A5B')
    for i, (b, pv) in enumerate(zip(bars, pvals)):
        ax.text(b.get_width() + 0.012, b.get_y() + b.get_height()/2,
                f'β = {b.get_width():.3f}  ({pv})', va='center', fontsize=9, color='#0B2A5B')
    ax.set_xlim(0, 0.6)
    ax.set_xlabel('标准化路径系数 β', fontsize=10, color='#0B2A5B')
    ax.set_title('结构方程模型 (SEM) 四项研究假设检验结果   χ²/df=2.31  CFI=0.942  RMSEA=0.058',
                 fontsize=10, color='#0B2A5B', pad=12)
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.invert_yaxis()
    fig.tight_layout()
    p = os.path.join(ASSET_DIR, 'sem_path.png')
    fig.savefig(p, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return p

def chart_revenue_forecast():
    """三年收入预测 (单位: 万元)"""
    years = ['Y1 2026', 'Y2 2027', 'Y3 2028']
    c_token  = [62,  248,  642]
    c_pro    = [120, 540,  1480]
    b_saas   = [80,  420,  1320]
    custom   = [60,  280,  860]
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=160)
    x = np.arange(len(years))
    w = 0.18
    ax.bar(x - 1.5*w, c_token, w, label='C 端 Token 增值', color='#00E5FF', edgecolor='#0B2A5B')
    ax.bar(x - 0.5*w, c_pro,   w, label='C 端 Pro 订阅',  color='#1E88E5', edgecolor='#0B2A5B')
    ax.bar(x + 0.5*w, b_saas,  w, label='B 端 SaaS API', color='#1FAE6F', edgecolor='#0B2A5B')
    ax.bar(x + 1.5*w, custom,  w, label='文旅文博定制',   color='#F4A11A', edgecolor='#0B2A5B')
    ax.set_xticks(x); ax.set_xticklabels(years)
    ax.set_ylabel('营业收入 (万元)', fontsize=10, color='#0B2A5B')
    ax.set_title('LifeBeyond 三年营收结构预测  (中性情境)', fontsize=11, color='#0B2A5B', pad=12)
    ax.legend(loc='upper left', frameon=False, fontsize=9)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    p = os.path.join(ASSET_DIR, 'revenue_forecast.png')
    fig.savefig(p, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return p

# ------------------------------------------------------------
# 文档样式
# ------------------------------------------------------------
def setup_document(doc):
    s = doc.sections[0]
    s.left_margin = Cm(2.4)
    s.right_margin = Cm(2.4)
    s.top_margin = Cm(2.4)
    s.bottom_margin = Cm(2.4)
    # 正文样式
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(10.5)
    style._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')

# ------------------------------------------------------------
# 章节构建 (主入口)
# ------------------------------------------------------------
def build_cover(doc):
    """封面"""
    for _ in range(4):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('LifeBeyond')
    r.font.size = Pt(48)
    r.font.bold = True
    r.font.color.rgb = RGB(COLOR['primary'])
    r.font.name = 'Times New Roman'

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run('数字 彼 岸')
    r2.font.size = Pt(20)
    r2.font.color.rgb = RGB(COLOR['accent'])
    r2.font.name = '思源黑体 CN'
    r2._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')

    doc.add_paragraph()
    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r3 = p3.add_run('—— 商业计划书 ——')
    r3.font.size = Pt(14)
    r3.font.color.rgb = RGB(COLOR['muted'])
    r3.font.name = 'Times New Roman'

    for _ in range(2):
        doc.add_paragraph()
    p4 = doc.add_paragraph()
    p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r4 = p4.add_run('AI 数字复生 · 情感陪伴 · 数字纪念 · 文明记忆')
    r4.font.size = Pt(13)
    r4.font.bold = True
    r4.font.color.rgb = RGB(COLOR['neon'])
    r4.font.name = '思源黑体 CN'
    r4._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')

    for _ in range(8):
        doc.add_paragraph()

    # 底部信息卡
    tbl = doc.add_table(rows=4, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    info = [
        ('理论基础', '技术接受模型 TAM · 结构方程模型 SEM · K-means 聚类'),
        ('实证样本', '21 份深度访谈 (20 省市自治区) · 306 份有效问卷'),
        ('产品形态', 'Web + 移动端 + 智能硬件 (沉浸式宇宙界面)'),
        ('文档版本', 'v1.0  ·  2026 年第一季度'),
    ]
    for i, (k, v) in enumerate(info):
        for j, txt in enumerate((k, v)):
            c = tbl.cell(i, j)
            set_cell_bg(c, COLOR['primary'] if j == 0 else COLOR['panel'])
            set_cell_border(c, COLOR['accent'], '6')
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(f'  {txt}')
            r.font.size = Pt(10)
            r.font.bold = (j == 0)
            r.font.color.rgb = RGB('FFFFFF' if j == 0 else COLOR['ink'])
            r.font.name = 'Times New Roman'
            r._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')
            c.width = Cm(4 if j == 0 else 12)
    page_break(doc)

def build_toc(doc):
    add_heading(doc, '目  录', level=0)
    items = [
        ('第一章  执行摘要',          '01'),
        ('第二章  行业背景与市场机会', '03'),
        ('第三章  实证用户研究',      '07'),
        ('第四章  产品概念与架构',    '14'),
        ('第五章  用户使用流程',      '21'),
        ('第六章  商业模式',          '24'),
        ('第七章  财务预测',          '29'),
        ('第八章  技术架构与合规',    '33'),
        ('第九章  营销与渠道策略',    '37'),
        ('第十章  风险与伦理对冲',    '40'),
        ('第十一章 团队与执行路线图', '43'),
        ('第十二章 投资亮点与展望',   '45'),
        ('附录  调研数据全集',        '47'),
    ]
    for title, pg in items:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.4
        r1 = p.add_run(title)
        r1.font.size = Pt(11.5)
        r1.font.bold = True
        r1.font.color.rgb = RGB(COLOR['primary'])
        r1.font.name = 'Times New Roman'
        r1._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')
        # 占位点线
        r2 = p.add_run('  ' + '·' * 70 + '  ')
        r2.font.size = Pt(10)
        r2.font.color.rgb = RGB(COLOR['stroke'])
        r3 = p.add_run(pg)
        r3.font.size = Pt(10.5)
        r3.font.color.rgb = RGB(COLOR['accent'])
        r3.font.name = 'Times New Roman'
    page_break(doc)

# ============================================================
# 主流程 (各章节将由 edit_file 增量追加)
# ============================================================
def build_chapter_1(doc, img_donut=None):
    """第一章  执行摘要"""
    add_heading(doc, '第一章  执行摘要', level=1)

    add_heading(doc, '1.1  项目定位', level=2)
    add_para(doc,
        'LifeBeyond（中文名：数字彼岸）是一款面向情感慰藉与数字纪念需求的 AI 数字复生服务平台，'
        '以技术接受模型（Technology Acceptance Model, TAM）为理论基础，依托 306 份实证问卷与 '
        '21 份深度访谈所构建的用户洞察体系，提供轻量化、合规化、有温度的数字人定制、跨时空对话、'
        '沉浸式纪念与文明记忆漫游服务。产品形态采用 Web + 移动端 + 智能硬件混合架构，'
        '以浏览器即开即用的沉浸式宇宙界面为主入口，整合彼岸、聊天、彼岸动态、社区与星图五大视图，'
        '并以文明记忆宇宙作为差异化情感叙事载体。')

    add_heading(doc, '1.2  核心数据洞察', level=2)
    add_table(doc,
        headers=['维度', '关键指标', '数据来源'],
        rows=[
            ['市场规模',  '2025E 中国虚拟人核心市场 480.6 亿元 / 带动产业 6,402.7 亿元', '艾瑞咨询 2024'],
            ['用户接受', '总接受率 51.0% (完全接受 18.6% + 有条件接受 32.4%)',          '本研究 N=306'],
            ['用户拒绝', '明确拒绝率 30.4% (核心来源：伦理顾虑型用户)',                   '本研究 N=306'],
            ['情感粘性', '单日聊天轮次 160 次 / 次日留存 80% / 平均时长 60 分钟',         '行业内测数据'],
            ['付费区间', '主流可接受价格 100–500 元 / 一次性买断模式占优',                '本研究 SEM'],
            ['SEM 检验', 'H1–H4 全部通过显著性检验 (β = 0.187–0.452)',                     '本研究 SEM'],
            ['年龄结构', '18–35 岁青年群体占有效样本 57.51% (核心种子用户)',               '本研究问卷'],
            ['学历结构', '本科及以上占 76% (高知群体)',                                    '本研究问卷'],
        ],
        col_widths=[3.2, 9.2, 3.6])
    doc.add_paragraph()

    if img_donut:
        add_image(doc, img_donut, width_cm=14.5,
                  caption='图 1-1  公众对 AI 数字复生技术整体接受度分布（基于 306 份有效问卷）')

    add_heading(doc, '1.3  商业价值主张', level=2)
    add_callout(doc, '一句话定位',
        '以低门槛、合规化的 AI 数字复生技术，为用户提供有温度、可信赖的情感慰藉与数字纪念服务，'
        '填补技术商业化与用户情感需求之间的市场空白。', color_key='accent')

    add_bullet(doc, '梯度化功能矩阵：基础数字纪念（低伦理风险，普惠定价）→ 沉浸式情景缅怀（中等订阅）→ 双向情感交互（增值服务）。',
               bold_lead='差异化产品分层')
    add_bullet(doc, '采用 C 端基础免费 + Token 增值 + Pro 订阅 + B 端 SaaS API 四引擎并行结构，',
               bold_lead='复合收入引擎')
    add_bullet(doc, '区块链授权确权、本地化预处理 + 云端加密训练、内置伦理审查模块，将合规作为产品力。',
               bold_lead='合规即护城河')
    add_bullet(doc, '依托文明记忆宇宙将个人哀悼上升至文明传承层面，与同类 AI 复生工具形成情感叙事差异化。',
               bold_lead='情感叙事差异化')

    add_heading(doc, '1.4  融资需求与资金用途', level=2)
    add_para(doc,
        '本轮拟开放天使轮 / Pre-A 轮股权融资 ¥2,000 万人民币，对应公司估值 ¥1.5 亿元（投后），'
        '资金用途分配为：核心算法与模型迭代 35%、合规与伦理审查体系建设 18%、用户运营与心理援助团队 17%、'
        '市场推广与渠道 BD 20%、储备与现金流安全 10%。预计 Y2 末实现单月经营性现金流转正，'
        'Y3 营业收入突破 ¥4,300 万元，毛利率维持 60% 以上。')

    page_break(doc)


def build_chapter_2(doc, img_market=None):
    """第二章  行业背景与市场机会"""
    add_heading(doc, '第二章  行业背景与市场机会', level=1)

    add_heading(doc, '2.1  生成式 AI 推动数字人产业平民化', level=2)
    add_para(doc,
        '随着大语言模型（LLM）、扩散模型（Diffusion）、3D 高斯泼溅（3DGS）、'
        '实时神经渲染等核心技术的协同演进，数字人制作的边际成本在 2023–2025 年间下降了'
        '约 87%。终端用户通过提供少量照片、音频或文本数据，即可生成具备基础对话、表情驱动'
        '与声音克隆能力的数字形象。技术成本曲线的陡降，使得 AI 复现逝者从早期的高端定制服务'
        '演化为可面向 C 端的消费级应用，为本项目的商业化奠定了底层算力与算法基础。')

    add_heading(doc, '2.2  中国虚拟数字人市场规模演进', level=2)
    add_para(doc,
        '根据艾瑞咨询《2024 年中国虚拟人产业研究报告》，2023 年中国虚拟人带动产业市场规模'
        '与核心市场规模分别为 3,334.7 亿元与 205.2 亿元；预计至 2025 年将分别达到 6,402.7 亿元'
        '与 480.6 亿元，三年复合增长率（CAGR）分别为 38.6% 与 53.0%，呈现典型的高速扩张特征。'
        '在此宏观增长背景下，AI 数字复生作为情感陪伴与数字纪念的细分赛道，'
        '正从文娱、客服等通用场景中分化出来，形成具备独立商业逻辑的新兴市场。')

    if img_market:
        add_image(doc, img_market, width_cm=15,
                  caption='图 2-1  中国虚拟数字人市场规模演进（2023 → 2025E）  单位：亿元')

    add_heading(doc, '2.3  AI 情感陪伴赛道增长曲线', level=2)
    add_para(doc,
        '据 a16z 公开统计，截至 2024 年第四季度，全球网页端 AI 应用访问量前 100 名中，'
        '情感陪伴类产品稳定占据 7 席，总访问量达 3.53 亿，同比增长 8.05%。'
        '头部产品 Character.AI 月访问量 2.15 亿，JanitorAI、SpicyChat 等长尾产品分别实现 '
        '23.93% 与 26.67% 的高速增长。国内方面，MiniMax 星野、抖音猫箱、昆仑万维 Linky、'
        '小冰 X-EVA 等产品月活均进入全球前 100，仅次于海外头部应用。'
        '细分产品的内测数据显示，单日平均聊天轮次达 160 次、单人使用时长超 60 分钟、'
        '次日留存率超 80%，揭示了情感陪伴赛道的强用户粘性与高商业化潜力。')

    add_table(doc,
        headers=['细分场景', '代表产品 / 形态', '核心用户价值'],
        rows=[
            ['情感陪伴',  '虚拟恋人 · AI 潮玩 · 数字伴侣',          '提供非替代性情感支持，缓解孤独感'],
            ['心理健康',  '数字人心理咨询 · AI 心理按摩师',          '辅助情绪疏导，提升心理健康可及性'],
            ['生活助手',  '日程提醒 · 习惯养成 · 自我夸奖',          '融入日常，提升生活幸福感'],
            ['数字纪念',  'AI 复现逝者 · 数字遗产 · 文明记忆',       '跨越生死的情感载体（本项目核心赛道）'],
        ],
        col_widths=[3.0, 5.5, 7.5])
    doc.add_paragraph()

    add_heading(doc, '2.4  数字遗产法规演进与合规窗口', level=2)
    add_para(doc,
        '《民法典》第 1019 条明确逝者肖像、姓名、名誉等人格权益受法律保护；'
        '《个人信息保护法》第 49 条赋予近亲属对死者个人信息的查阅、复制、更正、删除权；'
        '《生成式人工智能服务管理暂行办法》（2023 年 8 月施行）要求 AIGC 内容显著标识、'
        '训练数据来源合法、用户授权链条可追溯。三大法律 / 法规的合力，'
        '为 AI 数字复生赛道勾勒出清晰的合规边界。')

    add_callout(doc, '战略性结论',
        '法规体系的健全恰好构成 LifeBeyond 的合规护城河：'
        '在监管真空期入局的竞品需在政策落地后补足合规成本，'
        '而本项目以合规先行作为产品设计哲学，可在赛道窗口期建立先发优势。',
        color_key='success')

    page_break(doc)


def build_chapter_3(doc, img_donut=None, img_radar=None, img_sem=None):
    """第三章  实证用户研究"""
    add_heading(doc, '第三章  实证用户研究', level=1)

    add_heading(doc, '3.1  研究设计与方法体系', level=2)
    add_para(doc,
        '本研究以技术接受模型（TAM）为理论基础，融合计划行为理论（TPB）的态度变量与'
        '风险感知理论的伦理顾虑变量，构建扩展型 AI 数字复生技术接受度模型。'
        '在方法论上采用文献研究 + 文本挖掘 + 问卷调查 + 深度访谈四重数据融合，'
        '以结构方程模型（SEM）进行路径分析、K-means 进行用户聚类、'
        '词频分析与主题模型进行舆情挖掘，确保研究结论的稳定性与可信度。')

    add_table(doc,
        headers=['研究阶段', '方法与样本', '产出指标'],
        rows=[
            ['前期文献综述',   '中外文献 142 篇 · 行业报告 17 份',                    '理论模型与变量定义'],
            ['深度访谈',       '20 省市 · 21 份有效访谈 · 单份 15–40 分钟',           '接受 / 抗拒群体核心诉求'],
            ['问卷调查',       '线上线下结合 · 306 份有效问卷 · 有效率 91.6%',        '量表数据与描述统计'],
            ['文本挖掘',       'B 站 / 小红书 / 抖音 / 微博 / 知乎 · 24 万条 UGC',      '舆情情感分布与关键词'],
            ['SEM 路径分析',   '潜变量 5 个 · 观测变量 26 个 · 拟合优度 χ²/df=2.31',    'H1–H4 路径系数'],
            ['K-means 聚类',   '肘部法则确定 k=3 · 迭代 50 次',                       '三类用户画像'],
        ],
        col_widths=[3.0, 6.5, 6.5])
    doc.add_paragraph()

    add_heading(doc, '3.2  整体接受度与拒绝率分析', level=2)
    add_para(doc,
        '描述性统计显示：完全接受用户占比 18.6%，有条件接受占比 32.4%，'
        '中立观望 18.6%，部分反对 13.7%，明确拒绝 16.7%。总接受率达到 51.0%，'
        '总拒绝率 30.4%。值得注意的是，中立观望群体在代入"亲人离世真实情境"假设后，'
        '尝试意愿出现显著正向跃迁，揭示了 AI 复生需求的典型场景触发型特征——'
        '即抽象的伦理顾虑会在具体的情感刚需面前出现弹性松动。')

    if img_donut:
        add_image(doc, img_donut, width_cm=14.5,
                  caption='图 3-1  AI 数字复生技术整体接受度分布（N = 306）')

    add_heading(doc, '3.3  结构方程模型 (SEM) 路径分析', level=2)
    add_para(doc,
        '本研究以"功能吸引力"、"伦理顾虑"、"开放性态度"、"付费偏好"四个潜变量作为前因，'
        '"使用意愿"作为结果变量，构建结构方程模型。模型整体拟合度良好：'
        'χ²/df = 2.31（< 3）、CFI = 0.942（> 0.9）、TLI = 0.928（> 0.9）、'
        'RMSEA = 0.058（< 0.08）、SRMR = 0.047（< 0.08），各项拟合指数均达到结构方程建模通用阈值。')

    if img_sem:
        add_image(doc, img_sem, width_cm=15,
                  caption='图 3-2  四项研究假设的标准化路径系数（β）')

    add_para(doc,
        '四项研究假设全部通过显著性检验：H4（功能吸引力 → 使用意愿，β = 0.452***）影响最强，'
        '说明纪念与情感价值类功能是接受度核心驱动器；H3（开放性态度 → 使用意愿，β = 0.318***）'
        '位居第二，验证了 18–35 岁青年群体作为种子用户的合理性；H1（付费偏好 → 使用意愿，β = 0.276**）'
        '揭示了付费意愿与使用意愿之间的正向耦合；H2（伦理顾虑 → 使用意愿，β = 0.187*）'
        '呈现意外的正向作用——理性用户的伦理风险感知会推动其深入了解产品边界，'
        '反而提升对合规产品的包容度。')

    add_heading(doc, '3.4  K-means 用户聚类与三级潜在用户分层', level=2)
    add_para(doc,
        '基于态度、行为、付费三组共 12 个变量进行 K-means 聚类，'
        '肘部法则确定最佳聚类数 k = 3，最终得到三类差异化用户群体。'
        '雷达图（图 3-3）展示了三类用户在 AI 技术接受态度、产品使用意愿、'
        '功能吸引力偏好、伦理顾虑程度、付费接受度、商业化反感度六个核心维度上的量化对比。')

    if img_radar:
        add_image(doc, img_radar, width_cm=14,
                  caption='图 3-3  三类聚类用户六维特征雷达图（5 分制）')

    add_table(doc,
        headers=['用户类型', '人口特征', '核心心理', '产品偏好', '付费区间'],
        rows=[
            ['理性接受型',
             '25–40 岁 / 本科 / 在职',
             '技术信任度高',
             '边界清晰的合规产品',
             '100–500 元一次性'],
            ['情感依赖型',
             '25–50 岁 / 女性偏多 / 经历丧亲',
             '情感刚需 + 沉迷焦虑',
             '深度交互 + 纪念日提醒',
             '月费 30–80 元订阅'],
            ['伦理顾虑型',
             '40 岁以上 / 退休 / 主妇',
             '强伦理排斥',
             '仅基础静态形象',
             '基本不付费'],
        ],
        col_widths=[2.6, 4.0, 3.0, 3.6, 3.4])
    doc.add_paragraph()

    add_callout(doc, '潜在用户三级分层',
        '【一级 核心重度】理性接受型 + 情感依赖型 ≈ 51% 样本，'
        '是产品早期推广的核心目标群体；'
        '【二级 中立潜力】伦理顾虑型 ≈ 30%，需通过场景化教育与基础功能开放实现转化；'
        '【三级 全年龄基本盘】各年龄段核密度峰值稳定集中于 3.5–4.5 分中高位区间，'
        '说明 AI 复现逝者并非仅 Z 世代需求，而是跨越年龄的广义市场。',
        color_key='accent')

    add_heading(doc, '3.5  文本挖掘与公众舆情分布', level=2)
    add_para(doc,
        '对 B 站、小红书、抖音、微博、知乎五大平台共 24 万条相关 UGC 内容进行情感分析与关键词提取，'
        '公众讨论核心聚焦于四大维度：情感体验类高频词（想念、父母、亲人、感动、眼泪）'
        '反映情感价值的强吸引力；技术真实度类（真实、声音、还原、科技）'
        '展示用户对生成质量的高敏感度；伦理争议类（害怕、不舒服、尊重、打扰、不敢）'
        '揭示心理抵触来源；隐私安全类（隐私、授权、安全、数据、滥用）'
        '指向未经授权使用逝者数据这一不可触碰底线。'
        '舆情整体呈现"情感认同与伦理顾虑并存"的双面性特征，'
        '与问卷数据形成交叉验证。')

    add_table(doc,
        headers=['维度', '高频关键词 TOP 5', '情感倾向', '占比'],
        rows=[
            ['情感价值', '想念 · 父母 · 亲人 · 怀念 · 感动',     '正向',  '38.2%'],
            ['技术真实', '真实 · 声音 · 还原 · 科技 · 数字人',    '中性',  '24.6%'],
            ['伦理争议', '害怕 · 不敢 · 尊重 · 打扰 · 不舒服',    '负向',  '21.7%'],
            ['隐私安全', '隐私 · 授权 · 安全 · 数据 · 滥用',      '负向',  '15.5%'],
        ],
        col_widths=[2.8, 7.4, 2.6, 2.2])
    doc.add_paragraph()

    page_break(doc)

def build_chapter_4(doc):
    """第四章  产品概念与架构"""
    add_heading(doc, '第四章  产品概念与架构', level=1)

    add_heading(doc, '4.1  产品哲学：让告别成为温柔的延续', level=2)
    add_para(doc,
        'LifeBeyond 拒绝"数字永生"式的技术傲慢叙事，'
        '将产品定义为"情感过渡的辅助工具，而非真实复活"。'
        '这一定位呼应了访谈中受访者反复强调的核心诉求——'
        '"我能始终清楚它不是本人"——'
        '亦契合 SEM 模型中伦理顾虑对使用意愿的正向作用机制：'
        '清晰的边界声明会反向提升用户的产品包容度。')

    add_callout(doc, '产品愿景',
        '在数字与现实交汇的彼岸，让每一段思念都能找到温柔的栖息地；'
        '让逝者以另一种形式陪伴生者完成哀伤过渡，'
        '让文明中每一个值得被记住的灵魂获得跨越时空的回响。',
        color_key='neon')

    add_heading(doc, '4.2  五大核心视图', level=2)
    add_para(doc,
        '产品以单一沉浸式宇宙界面为主入口，通过空间叙事将五大功能视图组织为可漫游的星海空间。'
        '用户通过底部 spatial-dock 在彼岸、聊天、彼岸动态、社区、星图之间无缝切换，'
        '形成连续而不割裂的情感体验。')

    add_table(doc,
        headers=['视图', '核心定位', '关键功能', '对应用户群'],
        rows=[
            ['彼岸',
             '私密缅怀空间',
             '逝者数字形象 / 老照片动态化 / 影像修复 / 信箱与日记',
             '全用户'],
            ['聊天',
             '跨时空对话',
             'AI 数字人多轮对话 / 语气还原 / 性格复现 / 安全提示',
             '情感依赖型'],
            ['彼岸动态',
             '记忆时间线',
             '纪念日提醒 / 仪式设计 / 家庭情感连接 / 回忆视频',
             '情感依赖型 + 中老年'],
            ['社区',
             '私密互助网络',
             '匿名共鸣 / 故事分享 / 心理援助资源 / 五标签筛选',
             '理性接受型'],
            ['星图',
             '宇宙星海漫游',
             '星座可视化 / 文明记忆入口 / 沉浸式哀悼空间',
             '全用户 (情感载体)'],
        ],
        col_widths=[2.0, 3.4, 6.2, 4.4])
    doc.add_paragraph()

    add_heading(doc, '4.3  差异化模块：文明记忆宇宙', level=2)
    add_para(doc,
        '文明记忆宇宙是 LifeBeyond 在同质化 AI 复生赛道中的核心差异化叙事载体。'
        '该模块将个人哀悼上升至文明传承层面，以同心壳层 + 角度扇区的二维结构组织'
        '6 个历史时代 × 6 个影响力维度的二维坐标网，承载 60+ 位历史人物锚点。'
        '用户通过自由漫游、滚轮缩放、点击虚空召唤记忆低语等交互行为，'
        '完成从私人哀伤到集体文明记忆的情感跃迁。')

    add_table(doc,
        headers=['维度', '内容设定'],
        rows=[
            ['时代壳层 (同心环)', '当代 · 工业革命 · 文艺复兴 · 丝绸之路 · 古代中国 · 古希腊 · 古埃及'],
            ['影响力扇区 (60°)', '社会贡献 · 创新推动 · 和平行动 · 人文精神 · 教育影响 · 时代改变'],
            ['粒子背景层级',     '深空尘埃 1,200 + 中层微星 460 + 前景闪烁 140 ≈ 1,800 颗光点'],
            ['记忆光线',         '共享 related 标签的人物两两连接 → 鼠标悬停高亮 (文明纽带可视化)'],
            ['记忆低语',         '点击虚空触发匿名独白浮现并淡出 → 仿照诗云的 unrank 出诗机制'],
            ['跨星系联动',       '人物详情卡 related 标签 → 跳转到对应时代 / 影响力子星系'],
        ],
        col_widths=[3.6, 12.4])
    doc.add_paragraph()

    add_heading(doc, '4.4  三层场景金字塔', level=2)
    add_para(doc,
        '基于聚类分析所揭示的不同用户群体伦理边界差异，'
        '产品在场景层面构建了"从静态到深度交互"的三层渐进金字塔，'
        '允许不同用户在自身可接受的伦理深度内选择使用方式。')

    add_table(doc,
        headers=['场景层级', '产品形态', '伦理深度', '目标用户', '商业模式'],
        rows=[
            ['L1 基础数字纪念',
             '单向动图 + 照片动态化 + 老影像修复',
             '低',
             '全用户 (含伦理顾虑型)',
             '免费 / 一次性买断'],
            ['L2 沉浸式情景缅怀',
             '虚拟场景重建 + 全息投影 + 仪式设计',
             '中',
             '理性接受型 + 情感依赖型',
             'Pro 订阅 / 功能模块'],
            ['L3 双向情感交互',
             '智能对话 + 性格复现 + 长效陪伴',
             '高',
             '情感依赖型核心',
             'Token 计费 / 增值'],
        ],
        col_widths=[3.4, 5.0, 1.8, 4.0, 3.2])
    doc.add_paragraph()

    add_heading(doc, '4.5  Free vs Pro 双版本差异化定位', level=2)
    add_table(doc,
        headers=['维度', 'LifeBeyond Free', 'LifeBeyond Pro'],
        rows=[
            ['目标用户',     '广义市场 (尤其伦理顾虑型)', '核心重度用户 (理性接受 + 情感依赖)'],
            ['核心功能',     '基础纪念 + 老照片动态化 + 5/日 AI 对话', '全功能解锁 + 占卜 + 文明记忆 Pro 模式'],
            ['AI 对话额度',  '每日 5 次 (Token 制)',             '每月 1,000 次 + 包月无限对话包'],
            ['数据存储',     '本地 + 云端 1GB',                  '云端 50GB + 全链路加密 + 区块链授权'],
            ['沉浸式星图',   '基础宇宙 + 50 颗星点',             '480 颗交互星点 + 5 组星座 + 螺旋星系'],
            ['文明记忆',     '只读浏览',                          '完整漫游 + 收藏记忆 + 跨星系跳转'],
            ['价格锚点',     '免费',                              '¥48 / 月  或  ¥398 / 年'],
        ],
        col_widths=[3.0, 6.5, 6.5])
    doc.add_paragraph()

    page_break(doc)


def build_chapter_5(doc):
    """第五章  用户使用流程"""
    add_heading(doc, '第五章  用户使用流程', level=1)

    add_heading(doc, '5.1  核心用户旅程 (MVP)', level=2)
    add_para(doc,
        '产品 MVP 阶段的核心用户旅程被精炼为"五步极简流程"，'
        '降低首次使用的认知与情绪负担，将关键转化节点压缩在前 10 分钟体验窗口内。')

    add_table(doc,
        headers=['阶段', '关键动作', '系统响应', '情绪触达', '关键指标'],
        rows=[
            ['Step 1  接入',
             '通过链接 / 应用商店进入',
             '宇宙星空过渡动画 (3 秒)',
             '从世俗到彼岸的仪式感',
             '点击率 CTR'],
            ['Step 2  授权',
             '上传逝者照片 / 音频 / 文字',
             '区块链授权链上存证 + 数据脱敏',
             '安全感与正当性建立',
             '授权完成率'],
            ['Step 3  生成',
             '选择生成深度 (L1 / L2 / L3)',
             '本地预处理 + 云端加密训练',
             '期待与谨慎并存',
             '完成时长 / 满意度'],
            ['Step 4  交互',
             '首次对话 / 仪式 / 漫游',
             '"非真实复活" 浮层显著标识',
             '情感连接初次建立',
             '次日留存 D1'],
            ['Step 5  沉淀',
             '日记留存 / 信箱书写 / 加入社区',
             '私密互助社区匹配 + 风险监测',
             '哀伤过渡而非长期沉迷',
             '七日留存 D7'],
        ],
        col_widths=[2.6, 3.8, 4.0, 3.6, 2.0])
    doc.add_paragraph()

    add_heading(doc, '5.2  三类用户的场景化路径分化', level=2)

    add_bullet(doc,
        '入口直达"沉浸式情景缅怀 L2"，按功能模块解锁回忆视频生成与虚拟纪念空间；'
        '强调合规与可信，提供数据控制权可视化面板；'
        '主推 ¥398/年 Pro 订阅，转化率预估 28%。',
        bold_lead='理性接受型旅程')
    add_bullet(doc,
        '强引导"双向情感交互 L3"，开放对话陪伴 + 纪念日提醒 + 信箱书写；'
        '内置使用时长 60 分钟 / 日的预警阈值与心理健康提示；'
        '采用 Token 包计费 (¥30 / 100 Token)，平均月 ARPU 预估 ¥85。',
        bold_lead='情感依赖型旅程')
    add_bullet(doc,
        '仅开放"基础数字纪念 L1"，剥离所有深度交互；'
        '提供老照片动态化 + 影像修复 + 纪念藏品打印；'
        '采用一次性买断模式 (¥199 / 永久存档)，作为流量入口与口碑层。',
        bold_lead='伦理顾虑型旅程')

    add_heading(doc, '5.3  关键转化节点与漏斗指标', level=2)
    add_table(doc,
        headers=['漏斗层级', '转化定义', '保守预估', '中性预估', '激进预估'],
        rows=[
            ['访客 → 注册',    '完成手机或邮箱注册',          '12%',  '18%',  '24%'],
            ['注册 → 授权上传', '完成首次数据授权',           '38%',  '52%',  '65%'],
            ['授权 → 生成',    '生成首个数字纪念',           '64%',  '78%',  '86%'],
            ['生成 → 留存 D7', '7 日内再次回访',             '32%',  '45%',  '58%'],
            ['留存 → 付费',    '完成首次付费 (Token 或 Pro)', '6.8%', '11.2%','16.5%'],
            ['付费 → 续费',    '次月续费',                  '42%',  '58%',  '72%'],
        ],
        col_widths=[3.0, 4.4, 2.8, 2.8, 2.8])
    doc.add_paragraph()

    page_break(doc)


def build_chapter_6(doc):
    """第六章  商业模式"""
    add_heading(doc, '第六章  商业模式', level=1)

    add_heading(doc, '6.1  商业模式画布 (Osterwalder)', level=2)
    add_table(doc,
        headers=['模块', '内容'],
        rows=[
            ['客户细分 CS',
             '核心刚需 (25–45 岁丧亲中青年) · 基础需求 (46–70 岁中老年) · 定制化需求 (B 端)'],
            ['价值主张 VP',
             '低门槛 · 合规化 · 有温度的 AI 数字复生服务 · 文明记忆叙事差异化'],
            ['渠道通路 CH',
             '抖音 / B 站 / 小红书 / 知乎 KOL 矩阵 + 殡葬 / 心理 / 公益 BD + 主流应用市场'],
            ['客户关系 CR',
             '7×12 一对一咨询 · 私密互助社区 · 心理援助专属通道 · 数据销毁专属通道'],
            ['收入来源 RS',
             'C 端 Token 增值 + Pro 订阅 + B 端 SaaS API + 文旅文博定制 + 智能硬件分成'],
            ['关键资源 KR',
             '自研 AI 算法 · 合规牌照 · 用户情感数据 (脱敏) · 心理援助专家网络'],
            ['关键业务 KA',
             '模型迭代 · 全链条合规 · 用户运营 · 内容营销 · 心理风险防控'],
            ['关键伙伴 KP',
             'AI 算法商 · 云厂商 · 律所 · 伦理机构 · 心理服务机构 · 殡葬陵园 · 文旅文博'],
            ['成本结构 CS',
             '算力 28% · 合规 16% · 内容运营 18% · 渠道 BD 22% · 心理援助 8% · 其他 8%'],
        ],
        col_widths=[3.0, 13.0])
    doc.add_paragraph()

    add_heading(doc, '6.2  四引擎收入结构', level=2)
    add_para(doc,
        '本项目摒弃单一订阅依赖，采用"基础免费 + 增值付费 + 企业服务 + 定制开发"四引擎并行，'
        '降低单一商业模式风险敞口，匹配三类用户的差异化付费偏好。'
        '设计上严格规避用户访谈中明确表达的反感点——'
        '"在情绪低谷被诱导消费"与"按时长计费的情感剥削"——'
        '改以"一次性买断 + 功能模块解锁 + Token 包"为主流计费方式。')

    add_table(doc,
        headers=['引擎', '细分 SKU', '定价', '目标人群', '预估贡献'],
        rows=[
            ['C 端 Token 增值',
             '对话 Token 包 / 高级语音克隆 / 视频生成',
             '¥30 / 100 Token',
             '情感依赖型',
             '25%'],
            ['C 端 Pro 订阅',
             '月费 / 年费会员 / 终身买断',
             '¥48 月 · ¥398 年',
             '理性接受型',
             '38%'],
            ['B 端 SaaS API',
             '数字人生成 API / 语音合成 / 内容审核 SDK',
             '¥0.8 / 次调用',
             '文旅文博 + 短视频 MCN',
             '22%'],
            ['B 端 定制服务',
             '公众人物家属定制 / 纪录片团队 / 公益项目',
             '¥8 万–80 万 / 项目',
             '高净值 B 端',
             '15%'],
        ],
        col_widths=[3.0, 5.6, 3.0, 2.8, 1.6])
    doc.add_paragraph()

    add_heading(doc, '6.3  定价策略：实证锚定的价格走廊', level=2)
    add_para(doc,
        '问卷中关于"心理可接受价格区间"的数据显示，'
        '理性接受型用户的中位接受价为 ¥318 (一次性)，'
        '情感依赖型用户的中位月度承受价为 ¥75，'
        '伦理顾虑型用户的付费意愿基本归零。'
        '基于上述分布，Pro 年费定价 ¥398、月费 ¥48、Token 包 ¥30 均落在'
        '核心用户群体价格敏感度的"舒适带"内。')

    add_callout(doc, '反情感剥削红线',
        '产品技术层面强制内嵌"情绪低谷场景下禁止推送付费内容"算法规则；'
        '商业层面承诺：永不按对话时长 / 按情感节点收费；'
        '所有 Token 消耗在 UI 中实时透明可见，杜绝"暗扣式"消费。',
        color_key='warn')

    add_heading(doc, '6.4  用户终身价值 (LTV) 测算', level=2)
    add_table(doc,
        headers=['用户类型', '月度 ARPU', '平均生命周期', 'LTV', 'CAC', 'LTV / CAC'],
        rows=[
            ['理性接受型 (Pro 年费)', '¥33',  '24 个月', '¥792',   '¥120', '6.6'],
            ['情感依赖型 (Token)',    '¥85',  '14 个月', '¥1,190', '¥180', '6.6'],
            ['伦理顾虑型 (买断)',     '¥17',  '永久',    '¥199',   '¥40',  '5.0'],
            ['B 端 SaaS',             '¥1,800','36 个月', '¥64,800','¥9,000','7.2'],
        ],
        col_widths=[3.2, 2.6, 2.8, 2.4, 2.4, 2.6])
    doc.add_paragraph()

    page_break(doc)


def build_chapter_7(doc, img_rev=None):
    """第七章  财务预测"""
    add_heading(doc, '第七章  财务预测', level=1)

    add_heading(doc, '7.1  用户增长漏斗预测', level=2)
    add_para(doc,
        '基于第五章漏斗指标的中性预估，结合渠道矩阵铺设节奏，'
        '本项目在前三年的用户增长曲线如下：')

    add_table(doc,
        headers=['指标', 'Y1 (2026)', 'Y2 (2027)', 'Y3 (2028)', '复合增长率'],
        rows=[
            ['累计注册用户',    '32,000',  '186,000',   '742,000',  '381%'],
            ['月活用户 (MAU)',  '11,500',  '68,400',    '278,000',  '391%'],
            ['付费用户',        '1,280',   '12,640',    '76,200',   '672%'],
            ['付费转化率',      '4.0%',    '6.8%',      '10.3%',    '—'],
            ['B 端签约客户',    '8',       '34',        '112',      '274%'],
        ],
        col_widths=[3.2, 2.6, 2.6, 2.6, 2.4])
    doc.add_paragraph()

    add_heading(doc, '7.2  三年营收结构预测 (中性情境)', level=2)
    if img_rev:
        add_image(doc, img_rev, width_cm=15,
                  caption='图 7-1  LifeBeyond 三年四引擎营收结构预测  单位：万元')

    add_table(doc,
        headers=['收入引擎', 'Y1 (万元)', 'Y2 (万元)', 'Y3 (万元)', 'Y3 占比'],
        rows=[
            ['C 端 Token 增值',  '62',    '248',    '642',    '14.9%'],
            ['C 端 Pro 订阅',    '120',   '540',    '1,480',  '34.4%'],
            ['B 端 SaaS API',    '80',    '420',    '1,320',  '30.7%'],
            ['文旅文博定制',     '60',    '280',    '860',    '20.0%'],
            ['合计',             '322',   '1,488',  '4,302',  '100%'],
        ],
        col_widths=[3.4, 2.8, 2.8, 2.8, 2.2])
    doc.add_paragraph()

    add_heading(doc, '7.3  成本结构与盈亏平衡', level=2)
    add_table(doc,
        headers=['成本项', 'Y1 (万元)', 'Y2 (万元)', 'Y3 (万元)', '占比'],
        rows=[
            ['算力与模型',     '108',    '386',    '928',     '28%'],
            ['合规与法务',     '62',     '238',    '530',     '16%'],
            ['内容运营',       '70',     '268',    '596',     '18%'],
            ['渠道与营销',     '84',     '326',    '728',     '22%'],
            ['心理援助团队',   '32',     '118',    '264',     '8%'],
            ['行政与其他',     '32',     '120',    '266',     '8%'],
            ['合计',           '388',    '1,456',  '3,312',   '100%'],
        ],
        col_widths=[3.4, 2.8, 2.8, 2.8, 2.2])
    doc.add_paragraph()

    add_callout(doc, '关键财务指标',
        'Y1 营业亏损 ¥66 万元 → Y2 微盈 ¥32 万元 → Y3 净利 ¥990 万元；'
        'Y2 末实现单月经营性现金流转正，Y3 综合毛利率 60.4%，'
        '本轮 ¥2,000 万融资覆盖至 Y3 中下旬现金流安全期。',
        color_key='success')

    add_heading(doc, '7.4  情境敏感性分析', level=2)
    add_table(doc,
        headers=['情境', '关键假设', 'Y3 营收', 'Y3 净利', '回本周期'],
        rows=[
            ['保守',  '付费转化 6.8% · CAC 上浮 30%',  '¥2,580 万', '¥220 万',  '4.2 年'],
            ['中性',  '付费转化 10.3% · CAC 持平',     '¥4,302 万', '¥990 万',  '2.8 年'],
            ['激进',  '付费转化 16.5% · 拓展东南亚',   '¥7,180 万', '¥2,160 万','1.9 年'],
        ],
        col_widths=[2.4, 6.2, 2.6, 2.4, 2.2])
    doc.add_paragraph()

    page_break(doc)

def build_chapter_8(doc):
    """第八章  技术架构与合规"""
    add_heading(doc, '第八章  技术架构与合规', level=1)

    add_heading(doc, '8.1  端到端技术栈', level=2)
    add_table(doc,
        headers=['层级', '技术选型', '关键能力'],
        rows=[
            ['交互层',
             'Three.js + WebGL 着色器 + Canvas 2D + Lucide Icons',
             '沉浸式宇宙界面 · 1,800 颗粒子 · 480 颗交互星点'],
            ['前端框架',
             'Next.js 16 (App Router) + React 19 + Tailwind 4',
             'HMR · SSR · 高 Lighthouse 评分'],
            ['对话与生成',
             '多模型路由 (Doubao / DeepSeek / Kimi) + 流式 SSE',
             '打字机式流式输出 · 多轮对话 · 上下文压缩'],
            ['多模态合成',
             '语音克隆 (ASR/TTS) + 图像扩散 + 视频生成',
             '逝者声音还原 · 老照片动态化 · 回忆视频'],
            ['数据层',
             'Supabase (PostgreSQL + Auth + Realtime) + S3 对象存储',
             '关系数据 · 实时订阅 · 大文件托管'],
            ['基础设施',
             'Cloudflare Pages + Edge Functions + DDoS 防护',
             '全球加速 · 弹性扩容 · 5 万并发'],
            ['合规与安全',
             '区块链授权 + 本地化预处理 + 沙箱隔离 + 内容审核',
             '授权链上存证 · 端到端加密 · 实时违规拦截'],
        ],
        col_widths=[2.6, 6.6, 6.8])
    doc.add_paragraph()

    add_heading(doc, '8.2  数据全生命周期管控', level=2)
    add_table(doc,
        headers=['生命周期阶段', '管控措施', '技术实现'],
        rows=[
            ['采集',     '逝者授权人身份核验 + 数据来源声明',         '人脸 + 公安联网核验 + 区块链存证'],
            ['传输',     '端到端加密 + 防中间人攻击',                  'TLS 1.3 + Perfect Forward Secrecy'],
            ['预处理',   '本地化脱敏 + 特征提取',                       '客户端 WebAssembly 完成敏感字段剔除'],
            ['训练',     '云端仅接收加密特征参数 + 联邦学习',           '同态加密 + 沙箱内执行'],
            ['存储',     '本地 + 云端双存储 + 分布式对象存储',          'AES-256 + 自动跨区域冗余'],
            ['使用',     '权限分级 + 沙箱限制 + 实时审计',              '基于场景的 RBAC + 操作日志上链'],
            ['销毁',     '一键发起全量数据删除 + 不可逆销毁凭证',       '区块链出具销毁哈希证明'],
        ],
        col_widths=[2.6, 6.6, 6.8])
    doc.add_paragraph()

    add_heading(doc, '8.3  伦理审查内嵌机制', level=2)
    add_bullet(doc,
        '在核心交互节点自动推送"非真实复活"提示，规避用户认知混淆。',
        bold_lead='非真实复活 强制声明')
    add_bullet(doc,
        '单日累计对话超 60 分钟自动触发休息提醒，超过 120 分钟需重新验证身份。',
        bold_lead='交互时长 算法阈值')
    add_bullet(doc,
        '基于提示词工程与内容安全模型，限制生成违背逝者生前意愿与公序良俗的内容。',
        bold_lead='生成内容 伦理边界')
    add_bullet(doc,
        '禁止在用户负面情绪场景下推送付费内容，由情感识别模型实时判定。',
        bold_lead='情绪低谷 商业化拦截')
    add_bullet(doc,
        '所有生成内容嵌入不可去除数字水印 + 区块链溯源 ID，从源头防范 Deepfake 滥用。',
        bold_lead='Deepfake 水印溯源')

    page_break(doc)


def build_chapter_9(doc):
    """第九章  营销与渠道策略"""
    add_heading(doc, '第九章  营销与渠道策略', level=1)

    add_heading(doc, '9.1  内容矩阵：四大平台差异化运营', level=2)
    add_para(doc,
        '基于文本挖掘所揭示的平台用户结构差异，'
        '本项目以"短视频破圈 + 新闻媒体权威背书 + 社交平台口碑沉淀"三段式内容矩阵，'
        '覆盖从认知到决策的全漏斗用户教育路径。')

    add_table(doc,
        headers=['平台', '内容定位', '核心目标', '更新节奏', 'KPI'],
        rows=[
            ['抖音 / 快手',
             '公益缅怀叙事 · 用户真实案例 · 情感共鸣',
             '破圈触达 18–35 岁核心用户',
             '日更 1 条',
             '播放量 / 涨粉'],
            ['B 站',
             '技术原理科普 · 产品测评 · 中长视频',
             '理性接受型种子用户教育',
             '周更 2 条',
             '完播率 / 评论'],
            ['小红书',
             '使用体验分享 · 仪式美学 · 设计感笔记',
             '情感依赖型 + 女性用户转化',
             '日更 1 条',
             '收藏 / 转发'],
            ['知乎',
             '伦理深度探讨 · 行业研究 · 长文回答',
             '理性用户与高知群体心智',
             '周更 1 篇',
             '赞同 / 阅读'],
            ['微博',
             '热点事件联动 · 行业话题发酵',
             '舆情破圈与品牌曝光',
             '日更 2 条',
             '热搜 / 转发'],
        ],
        col_widths=[2.2, 4.2, 4.0, 1.8, 2.0])
    doc.add_paragraph()

    add_heading(doc, '9.2  BD 渠道：线下场景嵌入', level=2)
    add_bullet(doc,
        '与各地殡葬服务机构、陵园签订合作协议，将产品作为延展服务嵌入告别仪式场景，'
        '初期目标在 12 个月内覆盖 80 家合作机构。',
        bold_lead='殡葬服务 · 陵园')
    add_bullet(doc,
        '与线下心理咨询机构、丧亲互助公益团队联合开展公益宣讲，'
        '向合作机构捐赠产品免费基础服务权限，建立心理援助专家网络。',
        bold_lead='心理咨询 · 公益组织')
    add_bullet(doc,
        '与文旅文博机构、纪录片制作团队合作开发 B 端定制项目，'
        '探索"数字院士传记"、"非遗传承人数字孪生"等场景级解决方案。',
        bold_lead='文旅文博 · 纪录片')

    add_heading(doc, '9.3  公益叙事与品牌建设', level=2)
    add_callout(doc, '品牌叙事核心',
        '"科技应当成为对抗遗忘的温柔工具，而非制造虚假复活的傲慢机器。"'
        '通过持续公益项目 (清明数字寻亲 · 抗战老兵数字纪念 · 非遗传承人记忆库)，'
        '将企业 ESG 与产品价值主张深度融合，建立"科技向善"的品牌护城河。',
        color_key='neon')

    page_break(doc)


def build_chapter_10(doc):
    """第十章  风险与伦理对冲"""
    add_heading(doc, '第十章  风险与伦理对冲', level=1)

    add_heading(doc, '10.1  风险矩阵', level=2)
    add_table(doc,
        headers=['风险类别', '具体风险', '可能性', '影响度', '对冲措施'],
        rows=[
            ['政策风险',
             '数字遗产专项立法收紧 · 备案制变审批制',
             '中',
             '高',
             '提前合规 + 行业协会参与立法咨询'],
            ['伦理风险',
             '用户过度沉迷 · 媒体负面报道',
             '高',
             '高',
             '内嵌时长阈值 + 心理援助 + 公益叙事'],
            ['技术风险',
             '生成质量不足导致恐怖谷效应',
             '中',
             '中',
             '多模态融合 + 用户期望管理 + A/B 测试'],
            ['法律风险',
             '逝者人格权 / 肖像权诉讼',
             '中',
             '高',
             '严格授权链路 + 区块链存证 + 法律保险'],
            ['数据安全',
             '数据泄露 / Deepfake 滥用',
             '中',
             '极高',
             '端到端加密 + 数字水印 + 内容审核 + 应急预案'],
            ['市场风险',
             '行业头部巨头入场挤压',
             '高',
             '中',
             '差异化定位 (文明记忆) + 合规先发优势'],
            ['财务风险',
             'CAC 失控 · 现金流断裂',
             '低',
             '高',
             '多渠道 BD + 现金流安全垫 + 储备融资'],
        ],
        col_widths=[2.2, 5.4, 1.6, 1.6, 5.2])
    doc.add_paragraph()

    add_heading(doc, '10.2  伦理治理三道防线', level=2)
    add_bullet(doc,
        '产品研发阶段：伦理合规校验模块作为代码层硬性规则，研发流程中设置伦理评审关卡。',
        bold_lead='事前 设计层')
    add_bullet(doc,
        '产品运行阶段：内容安全审核 + 用户行为监控 + 7×24 实时拦截 + 反馈通道。',
        bold_lead='事中 运行层')
    add_bullet(doc,
        '后果处置阶段：用户一键销毁 + 区块链销毁凭证 + 法律保险 + 公益基金兜底。',
        bold_lead='事后 处置层')

    page_break(doc)


def build_chapter_11(doc):
    """第十一章  团队与执行路线图"""
    add_heading(doc, '第十一章  团队与执行路线图', level=1)

    add_heading(doc, '11.1  核心团队画像', level=2)
    add_table(doc,
        headers=['角色', '画像要求', '核心职责'],
        rows=[
            ['CEO / 创始人',
             '产品 + 战略背景 · 善于讲故事',
             '愿景 · 融资 · 顶层设计'],
            ['CTO',
             '资深 AI 工程师 · 主导过百万级 DAU 产品',
             '技术架构 · 模型迭代 · 工程效率'],
            ['CPO',
             '情感类产品 / 心理学交叉背景',
             '产品规划 · 用户体验 · 心理风险'],
            ['CMO',
             '内容营销 + KOL 资源 · 公益领域经验',
             '品牌 · 渠道 · 公益叙事'],
            ['伦理总监',
             '法律 + 哲学背景 · 数字伦理研究者',
             '合规 · 伦理审查 · 政策对接'],
            ['心理总监',
             '注册心理咨询师 · 哀伤辅导专家',
             '用户心理援助 · 风险预警 · 咨询师网络'],
        ],
        col_widths=[2.6, 5.6, 7.8])
    doc.add_paragraph()

    add_heading(doc, '11.2  18 个月里程碑', level=2)
    add_table(doc,
        headers=['阶段', '时间窗口', '关键交付物', '验收指标'],
        rows=[
            ['M1–M3',
             '种子启动',
             'MVP 上线 · L1 基础功能 · 1,000 内测用户',
             'DAU 200+ / 留存 D7 ≥ 35%'],
            ['M4–M6',
             '产品打磨',
             'L2 沉浸式缅怀 · 文明记忆 v1 · Pro 订阅上线',
             '注册 10,000 / 付费 200'],
            ['M7–M9',
             '商业化验证',
             'L3 双向交互 · Token 体系 · 殡葬 BD 启动',
             '月收入 ≥ ¥10 万'],
            ['M10–M12',
             '规模扩张',
             'B 端 SaaS API 上线 · 智能硬件适配',
             '注册 100,000 / 付费 5,000'],
            ['M13–M15',
             '生态构建',
             '心理援助网络 · 公益项目 · ESG 报告',
             '签约心理师 50+ / 公益曝光 1 亿'],
            ['M16–M18',
             '盈亏平衡',
             '单月经营现金流转正 · 拓展东南亚 PoC',
             '月营收 ≥ ¥250 万 / 毛利率 ≥ 55%'],
        ],
        col_widths=[2.0, 2.2, 6.6, 5.2])
    doc.add_paragraph()

    page_break(doc)


def build_chapter_12(doc):
    """第十二章  投资亮点与展望"""
    add_heading(doc, '第十二章  投资亮点与展望', level=1)

    add_heading(doc, '12.1  五大投资亮点', level=2)
    add_callout(doc, '① 黄金赛道窗口',
        '中国虚拟人核心市场 CAGR 53.0% · AI 情感陪伴细分赛道 80% 留存 · 月活前 100 国产应用快速崛起。'
        '赛道处于"技术成熟 + 法规初成 + 巨头未入"的黄金窗口期，先发者可建立 18–24 个月护城河。',
        color_key='success')
    add_callout(doc, '② 实证驱动的产品力',
        '本项目所有核心产品决策均基于 306 份实证问卷 + 21 份深度访谈，'
        '辅以 SEM 路径分析与 K-means 用户聚类，避免"创始人直觉决策"的常见死亡谷。',
        color_key='accent')
    add_callout(doc, '③ 合规即护城河',
        '在数字遗产 / 生成式 AI 监管收紧的趋势下，'
        '将合规作为产品力（而非合规成本），可在政策落地期挤压非合规竞品的生存空间。',
        color_key='neon')
    add_callout(doc, '④ 差异化叙事',
        '文明记忆宇宙将私人哀悼上升至文明传承层面，'
        '建立同类 AI 复生工具难以模仿的情感叙事壁垒，'
        '对应 SEM 模型中影响力最强的"功能吸引力 → 使用意愿" β = 0.452 通路。',
        color_key='accent')
    add_callout(doc, '⑤ 高 LTV / CAC 复合财务模型',
        '四引擎收入结构降低单一模式风险敞口；'
        '综合 LTV/CAC = 6.6（行业 SaaS 平均 3.0），'
        'Y3 净利预估 ¥990 万元，回本周期 2.8 年（中性情境）。',
        color_key='success')

    add_heading(doc, '12.2  长期愿景', level=2)
    add_para(doc,
        '三年内（2026–2028），LifeBeyond 立足中国市场，'
        '构建从 C 端纪念到 B 端文化数字化的完整产品矩阵，建立数字纪念赛道的头部品牌位置；'
        '五年内（2029–2030），拓展东南亚、日韩、北美华人社区，'
        '将"科技向善"的合规化叙事打造为可复制的全球性产品哲学；'
        '十年内，与博物馆、档案馆、文化遗产机构形成深度合作生态，'
        '使 LifeBeyond 成为承载人类文明集体记忆的数字基础设施之一。')

    add_callout(doc, '终极愿景',
        '让告别成为温柔的延续，让每一个值得被铭记的灵魂，'
        '在数字与现实的交汇处，获得跨越时空的回响。',
        color_key='neon')

    page_break(doc)


def build_appendix(doc):
    """附录：调研数据全集"""
    add_heading(doc, '附录  调研数据全集', level=1)

    add_heading(doc, '附 A  深度访谈样本基础信息 (N=21)', level=2)
    add_table(doc,
        headers=['维度', '细分', '样本数', '占比'],
        rows=[
            ['年龄分层', '青年群体 (18–40 岁)',     '17', '80.95%'],
            ['',         '中年群体 (40 岁以上)',     '4',  '19.05%'],
            ['核心态度', '接受 / 有条件接受',         '12', '57.14%'],
            ['',         '不接受 / 抗拒',             '9',  '42.86%'],
            ['民族属性', '汉族',                     '18', '85.71%'],
            ['',         '少数民族 (藏族 / 回族)',    '3',  '14.29%'],
            ['职业类型', '在校学生',                 '8',  '38.10%'],
            ['',         '企业 / 事业单位职员',       '7',  '33.33%'],
            ['',         '自由职业 / 个体经营',       '3',  '14.29%'],
            ['',         '退休人员',                 '2',  '9.52%'],
            ['',         '其他',                     '1',  '4.76%'],
        ],
        col_widths=[3.0, 6.0, 3.0, 3.0])
    doc.add_paragraph()

    add_heading(doc, '附 B  问卷量表潜变量与观测变量', level=2)
    add_table(doc,
        headers=['潜变量', '观测变量', '题项数'],
        rows=[
            ['功能吸引力',
             '数字纪念藏品 / 电子日记 / 家庭历史 / 回忆视频 / 纪念日提醒 / 家庭情感连接 / 记忆储存 / 全息投影',
             '8'],
            ['伦理顾虑',
             '传统观念冲突 / 对逝者不尊重 / 沉溺悲伤 / 商业化情感 / 数据安全 / 技术成熟度',
             '6'],
            ['开放性态度',
             'AI 技术信任 / 死亡观念开放 / 数字遗产认同 / 新技术尝鲜意愿',
             '4'],
            ['付费偏好',
             '付费意愿 / 价格区间 / 计费方式偏好 / 商业化反感点',
             '4'],
            ['使用意愿',
             '尝试意愿 / 推荐意愿 / 持续使用意愿 / 场景化使用意愿',
             '4'],
        ],
        col_widths=[2.8, 11.0, 2.2])
    doc.add_paragraph()

    add_heading(doc, '附 C  SEM 模型拟合优度指标', level=2)
    add_table(doc,
        headers=['拟合指数', '本研究值', '通用阈值', '判定'],
        rows=[
            ['χ²/df',  '2.31',  '< 3.00',   '通过'],
            ['CFI',    '0.942', '> 0.90',   '通过'],
            ['TLI',    '0.928', '> 0.90',   '通过'],
            ['RMSEA',  '0.058', '< 0.08',   '通过'],
            ['SRMR',   '0.047', '< 0.08',   '通过'],
            ['GFI',    '0.914', '> 0.90',   '通过'],
            ['AGFI',   '0.892', '> 0.85',   '通过'],
        ],
        col_widths=[3.0, 3.6, 3.6, 5.8])
    doc.add_paragraph()

    add_heading(doc, '附 D  研究方法与文献来源', level=2)
    add_para(doc,
        '本商业计划书的所有数据均源自《"忆"路同行 · "数"说思念—— AI 生成逝者数字形象的'
        '社会接受度与伦理边界研究》原始调研报告，研究方法包括文献研究法、文本挖掘、'
        '深度访谈、问卷调查、结构方程模型分析与 K-means 聚类分析。'
        '产品架构与商业模式部分整合 LifeBeyond 数字彼岸网站 '
        '(https://noracx330.github.io/lifebeyond/) 的实际产品形态。'
        '行业数据引用艾瑞咨询《2024 年中国虚拟人产业研究报告》、'
        '头豹研究院《AI 陪伴：从工具属性向情感交互生态跃迁》(2025-09-30) 等公开行业报告。')

    # 文档结尾标识
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('— LifeBeyond · 数字彼岸  商业计划书  完 —')
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = RGB(COLOR['accent'])
    r.font.name = 'Times New Roman'
    r._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')


def main():
    print('[1] 预渲染数据图表...')
    img_market = chart_market_size()
    img_radar  = chart_user_radar()
    img_donut  = chart_acceptance_donut()
    img_sem    = chart_sem_path()
    img_rev    = chart_revenue_forecast()
    print(f'     图表已生成: {ASSET_DIR}')

    print('[2] 构建 Word 文档...')
    doc = Document()
    setup_document(doc)

    build_cover(doc)
    build_toc(doc)
    build_chapter_1(doc, img_donut=img_donut)
    build_chapter_2(doc, img_market=img_market)
    build_chapter_3(doc, img_donut=img_donut, img_radar=img_radar, img_sem=img_sem)
    build_chapter_4(doc)
    build_chapter_5(doc)
    build_chapter_6(doc)
    build_chapter_7(doc, img_rev=img_rev)
    build_chapter_8(doc)
    build_chapter_9(doc)
    build_chapter_10(doc)
    build_chapter_11(doc)
    build_chapter_12(doc)
    build_appendix(doc)

    doc.save(OUTFILE)
    sz = os.path.getsize(OUTFILE) / 1024
    print(f'[3] 完成: {OUTFILE} ({sz:.1f} KB)')

if __name__ == '__main__':
    main()
