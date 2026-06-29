#!/usr/bin/env python3
"""LifeBeyond Roadshow PPT Generator — Blue Tech Style"""

import os, math, io
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt
import numpy as np

# ── Palette ──────────────────────────────────────────────────────────────
BG_DARK   = RGBColor(0x08, 0x14, 0x2B)   # deep navy
BG_MID    = RGBColor(0x0C, 0x1D, 0x3E)   # mid navy
ACCENT    = RGBColor(0x48, 0x74, 0xCB)   # primary blue
ACCENT_LT = RGBColor(0x6B, 0xA3, 0xF7)   # light blue
ACCENT2   = RGBColor(0x00, 0xE5, 0xFF)   # cyan
GOLD      = RGBColor(0xC9, 0x97, 0x67)   # warm gold
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
LGRAY     = RGBColor(0xA6, 0xAD, 0xB8)   # light gray text
DGRAY     = RGBColor(0x3A, 0x4A, 0x5C)   # dim gray
SUCCESS   = RGBColor(0x6A, 0x9B, 0x7D)   # muted green
WARN      = RGBColor(0xB0, 0x55, 0x6C)   # muted red
MPL_BG    = '#0C1D3E'
MPL_ACC   = '#4874CB'
MPL_ACC2  = '#6BA3F7'

OUT = '/workspace/projects/public/LifeBeyond_Roadshow.pptx'

# ── Helpers ──────────────────────────────────────────────────────────────
prs = Presentation()
prs.slide_width  = Emu(12192000)   # 16:9
prs.slide_height = Emu(6858000)
SW = 12192000
SH = 6858000

def add_bg(slide, color=BG_DARK):
    """Set solid background color."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_shape(slide, left, top, width, height, fill_color=None, line_color=None, line_width=Pt(0)):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.line.fill.background()
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = line_width
    return shape

def add_rounded_rect(slide, left, top, width, height, fill_color=None, line_color=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.line.fill.background()
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(1.5)
    return shape

def add_text_box(slide, left, top, width, height, text, font_size=14, color=WHITE,
                 bold=False, alignment=PP_ALIGN.LEFT, font_name='Microsoft YaHei'):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    return txBox

def add_para(tf, text, font_size=12, color=WHITE, bold=False, alignment=PP_ALIGN.LEFT,
             space_before=Pt(4), space_after=Pt(2), font_name='Microsoft YaHei'):
    p = tf.add_paragraph()
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    p.space_before = space_before
    p.space_after = space_after
    return p

def add_accent_line(slide, left, top, width, color=ACCENT):
    """Horizontal accent line."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Pt(3))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape

def add_top_bar(slide, title_text, subtitle_text=''):
    """Common top bar with gradient-like accent."""
    # Top accent strip
    add_shape(slide, 0, 0, SW, Pt(4), fill_color=ACCENT)
    # Title
    add_text_box(slide, Inches(0.6), Inches(0.3), Inches(10), Inches(0.5),
                 title_text, font_size=26, color=WHITE, bold=True)
    if subtitle_text:
        add_text_box(slide, Inches(0.6), Inches(0.75), Inches(10), Inches(0.3),
                     subtitle_text, font_size=13, color=LGRAY)
    # Separator
    add_accent_line(slide, Inches(0.6), Inches(1.1), Inches(2), ACCENT)

def make_chart(fig_func, filename):
    """Generate chart image via matplotlib."""
    path = f'/tmp/bp_assets/{filename}'
    fig = fig_func()
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return path

def add_kpi_card(slide, left, top, width, height, label, value, sub='', fill=BG_MID, accent=ACCENT):
    card = add_rounded_rect(slide, left, top, width, height, fill_color=fill, line_color=accent)
    add_text_box(slide, left + Inches(0.15), top + Inches(0.1), width - Inches(0.3), Inches(0.25),
                 label, font_size=10, color=LGRAY)
    add_text_box(slide, left + Inches(0.15), top + Inches(0.35), width - Inches(0.3), Inches(0.35),
                 value, font_size=22, color=WHITE, bold=True)
    if sub:
        add_text_box(slide, left + Inches(0.15), top + Inches(0.7), width - Inches(0.3), Inches(0.2),
                     sub, font_size=9, color=LGRAY)

# ── Chart generators ─────────────────────────────────────────────────────
def chart_market():
    fig, ax = plt.subplots(figsize=(5.5, 3.2), facecolor=MPL_BG)
    ax.set_facecolor(MPL_BG)
    years = ['2022', '2023', '2024E', '2025E']
    vals = [186, 253, 358, 481]
    colors = ['#3A5A9C', '#4874CB', '#6BA3F7', '#00E5FF']
    bars = ax.bar(years, vals, color=colors, width=0.55, edgecolor='none')
    for b, v in zip(bars, vals):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+8, f'{v}', ha='center', color='white', fontsize=11, fontweight='bold')
    ax.set_ylabel('亿元', color='#A6ADB8', fontsize=10)
    ax.set_title('中国虚拟数字人核心市场规模', color='white', fontsize=13, pad=12)
    ax.tick_params(colors='#A6ADB8')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#3A4A5C')
    ax.spines['bottom'].set_color('#3A4A5C')
    ax.set_ylim(0, 560)
    return fig

def chart_user_segments():
    fig, ax = plt.subplots(figsize=(4, 3.2), facecolor=MPL_BG)
    ax.set_facecolor(MPL_BG)
    labels = ['理性接受型\n36.6%', '情感依赖型\n33.0%', '伦理顾虑型\n30.4%']
    sizes = [36.6, 33.0, 30.4]
    colors = ['#4874CB', '#C99767', '#6A9B7D']
    explode = (0.04, 0.04, 0.04)
    wedges, texts = ax.pie(sizes, labels=labels, colors=colors, explode=explode,
                           textprops={'color':'white', 'fontsize':10},
                           startangle=90, pctdistance=0.75)
    ax.set_title('三类用户群体占比 (K-Means k=3)', color='white', fontsize=12, pad=10)
    return fig

def chart_funnel():
    fig, ax = plt.subplots(figsize=(5.5, 3.2), facecolor=MPL_BG)
    ax.set_facecolor(MPL_BG)
    stages = ['认知\n100%', '接受\n47%', '尝试\n33%', '持续\n24%', '付费\n22%']
    vals = [100, 47, 33, 24, 22]
    colors = ['#00E5FF', '#6BA3F7', '#4874CB', '#3A5A9C', '#C99767']
    for i, (s, v) in enumerate(zip(stages, vals)):
        w = v / 100 * 6
        ax.barh(len(vals)-1-i, w, height=0.7, color=colors[i], left=(6-w)/2)
        ax.text(3, len(vals)-1-i, s, ha='center', va='center', color='white', fontsize=11, fontweight='bold')
    ax.set_xlim(0, 6)
    ax.set_title('认知-付费转化漏斗 (N=306)', color='white', fontsize=13, pad=12)
    ax.axis('off')
    return fig

def chart_revenue():
    fig, ax = plt.subplots(figsize=(5.5, 3.2), facecolor=MPL_BG)
    ax.set_facecolor(MPL_BG)
    years = ['Y1', 'Y2', 'Y3']
    token = [62, 248, 642]
    sub   = [120, 540, 1480]
    b2b   = [80, 420, 1320]
    custom= [60, 280, 860]
    x = np.arange(len(years))
    w = 0.18
    bars1 = ax.bar(x-1.5*w, token, w, color='#4874CB', label='C端Token')
    bars2 = ax.bar(x-0.5*w, sub,   w, color='#6BA3F7', label='C端Pro订阅')
    bars3 = ax.bar(x+0.5*w, b2b,   w, color='#C99767', label='B端SaaS')
    bars4 = ax.bar(x+1.5*w, custom,w, color='#6A9B7D', label='文旅定制')
    for bars in [bars1, bars2, bars3, bars4]:
        for b in bars:
            ax.text(b.get_x()+b.get_width()/2, b.get_height()+15, f'{int(b.get_height())}',
                    ha='center', color='white', fontsize=8, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(years, color='#A6ADB8')
    ax.set_ylabel('万元', color='#A6ADB8', fontsize=10)
    ax.set_title('三年营收结构预测 (中性情境)', color='white', fontsize=13, pad=12)
    ax.tick_params(colors='#A6ADB8')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#3A4A5C')
    ax.spines['bottom'].set_color('#3A4A5C')
    ax.legend(fontsize=9, loc='upper left', facecolor=MPL_BG, edgecolor='#3A4A5C', labelcolor='white')
    return fig

def chart_ltv():
    fig, ax = plt.subplots(figsize=(5.5, 3), facecolor=MPL_BG)
    ax.set_facecolor(MPL_BG)
    cats = ['理性接受型', '情感依赖型', '伦理顾虑型', 'B端SaaS']
    ltv  = [792, 1190, 199, 64800]
    cac  = [120, 180, 40, 9000]
    ratio= [6.6, 6.6, 5.0, 7.2]
    x = np.arange(len(cats))
    w = 0.3
    b1 = ax.bar(x-w/2, [v/10 for v in ltv], w, color='#4874CB', label='LTV (÷10)')
    b2 = ax.bar(x+w/2, [v/10 for v in cac], w, color='#C99767', label='CAC (÷10)')
    for i, r in enumerate(ratio):
        ax.text(i, max(ltv[i], cac[i])/10 + 50, f'LTV/CAC={r}', ha='center', color='#00E5FF', fontsize=10, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(cats, color='#A6ADB8', fontsize=9)
    ax.set_title('LTV / CAC 对比', color='white', fontsize=13, pad=12)
    ax.tick_params(colors='#A6ADB8')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#3A4A5C')
    ax.spines['bottom'].set_color('#3A4A5C')
    ax.legend(fontsize=9, loc='upper left', facecolor=MPL_BG, edgecolor='#3A4A5C', labelcolor='white')
    return fig

def chart_card_pool():
    fig, ax = plt.subplots(figsize=(4.5, 3), facecolor=MPL_BG)
    ax.set_facecolor(MPL_BG)
    rarities = ['N', 'R', 'SR', 'SSR']
    probs = [55, 28, 13, 4]
    colors = ['#3A5A9C', '#4874CB', '#6BA3F7', '#C99767']
    bars = ax.bar(rarities, probs, color=colors, width=0.55)
    for b, v in zip(bars, probs):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+1.2, f'{v}%', ha='center', color='white', fontsize=11, fontweight='bold')
    ax.set_ylabel('概率 %', color='#A6ADB8', fontsize=10)
    ax.set_title('剧情卡池稀有度分布', color='white', fontsize=12, pad=10)
    ax.tick_params(colors='#A6ADB8')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#3A4A5C')
    ax.spines['bottom'].set_color('#3A4A5C')
    ax.set_ylim(0, 65)
    return fig

# ── Generate chart images ────────────────────────────────────────────────
os.makedirs('/tmp/bp_assets', exist_ok=True)
print('Generating charts...')
charts = {
    'market':    make_chart(chart_market, 'ppt_market.png'),
    'segments':  make_chart(chart_user_segments, 'ppt_segments.png'),
    'funnel':    make_chart(chart_funnel, 'ppt_funnel.png'),
    'revenue':   make_chart(chart_revenue, 'ppt_revenue.png'),
    'ltv':       make_chart(chart_ltv, 'ppt_ltv.png'),
    'cardpool':  make_chart(chart_card_pool, 'ppt_cardpool.png'),
}
print('Charts done.')

# ═══════════════════════════════════════════════════════════════════════
# SLIDE 1 — COVER
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
add_bg(slide, BG_DARK)
# Gradient overlay strip at top
add_shape(slide, 0, 0, SW, Inches(0.08), fill_color=ACCENT)
# Subtle decorative line
add_shape(slide, 0, Inches(4.8), SW, Pt(2), fill_color=DGRAY)

add_text_box(slide, Inches(0.8), Inches(1.0), Inches(8), Inches(0.6),
             'LifeBeyond', font_size=44, color=ACCENT_LT, bold=True)
add_text_box(slide, Inches(0.8), Inches(1.65), Inches(8), Inches(0.5),
             '数 字 彼 岸', font_size=28, color=WHITE, bold=True)
add_text_box(slide, Inches(0.8), Inches(2.3), Inches(8), Inches(0.4),
             '—— AI 情感陪伴 · 数字纪念 · 文明记忆 ——', font_size=14, color=LGRAY)

add_accent_line(slide, Inches(0.8), Inches(2.85), Inches(3), ACCENT)

add_text_box(slide, Inches(0.8), Inches(3.1), Inches(8), Inches(0.3),
             '商 业 计 划 书 · 路 演 版', font_size=18, color=GOLD, bold=True)
add_text_box(slide, Inches(0.8), Inches(3.6), Inches(8), Inches(0.25),
             'Live Demo: https://noracx330.github.io/lifebeyond/', font_size=11, color=LGRAY)
add_text_box(slide, Inches(0.8), Inches(3.9), Inches(8), Inches(0.25),
             '已上线公开访问 · MVP 已交付 · 可直接体验', font_size=11, color=SUCCESS)

# Right side - key KPIs
add_kpi_card(slide, Inches(8.5), Inches(1.2), Inches(3.2), Inches(0.95),
             '市场规模', '480.6 亿', '2025E 中国虚拟人核心市场')
add_kpi_card(slide, Inches(8.5), Inches(2.35), Inches(3.2), Inches(0.95),
             '用户接受率', '51.0%', 'N=306 实证问卷')
add_kpi_card(slide, Inches(8.5), Inches(3.5), Inches(3.2), Inches(0.95),
             'LTV / CAC', '6.6x', '远超行业 SaaS 平均')

add_text_box(slide, Inches(0.8), Inches(5.0), Inches(10), Inches(0.25),
             '2025 年 6 月', font_size=11, color=DGRAY)

# ═══════════════════════════════════════════════════════════════════════
# SLIDE 2 — EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, BG_DARK)
add_top_bar(slide, '执行摘要', 'Executive Summary')

# One-liner
add_text_box(slide, Inches(0.6), Inches(1.3), Inches(11.5), Inches(0.4),
             '以低门槛、合规化的 AI 情感陪伴技术，为用户提供有温度、可信赖的思念寄托工具',
             font_size=15, color=ACCENT_LT, bold=True)

# 4 KPI cards row
cards = [
    ('市场规模', '480.6 亿', '2025E 核心市场', ACCENT),
    ('实证样本', '306 份', '4 项假设 p<0.001', ACCENT),
    ('用户接受率', '51.0%', '18.6% 完全接受', SUCCESS),
    ('LTV / CAC', '6.6x', '远超 SaaS 均值', GOLD),
]
for i, (label, value, sub, color) in enumerate(cards):
    left = Inches(0.6 + i * 2.85)
    add_kpi_card(slide, left, Inches(1.9), Inches(2.55), Inches(1.0), label, value, sub, accent=color)

# Key points
points = [
    '产品定位：AI 情感陪伴数字平台，拒绝"技术万能"叙事，定义为"思念陪伴辅助工具"',
    '实证驱动：基于 TAM 模型 + SEM 路径分析 + K-means 聚类，4 项假设全部 p<0.001',
    '已上线 MVP：6 个核心视图全部交付，Lighthouse Performance 92 / A11y 95 / SEO 100',
    '商业模式：四引擎收入（C端Token + Pro订阅 + B端SaaS + 文旅定制），Y3 营收 ¥4,302 万',
    '伦理护城河：反情感剥削算法硬嵌入，"在情绪低谷禁止推送付费内容"写入代码层',
]
for j, pt in enumerate(points):
    y = Inches(3.15 + j * 0.38)
    add_text_box(slide, Inches(0.8), y, Inches(11), Inches(0.35),
                 f'▸  {pt}', font_size=11, color=WHITE)

# ═══════════════════════════════════════════════════════════════════════
# SLIDE 3 — MARKET OPPORTUNITY
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, BG_DARK)
add_top_bar(slide, '行业背景与市场机会', 'Market Opportunity')

slide.shapes.add_picture(charts['market'], Inches(5.8), Inches(1.4), Inches(6.5), Inches(3.8))

bullets = [
    ('市场规模', '2025E 中国虚拟人核心市场 480.6 亿元，带动产业 1,834 亿元'),
    ('成本下降', '数字人制作边际成本 2023-2025 年下降约 87%，技术平民化拐点已至'),
    ('政策驱动', '《互联网信息服务深度合成管理规定》2023 年施行，合规先发者获护城河'),
    ('赛道空白', '数字纪念（AI 陪伴思念之人）为 4 大场景中唯一无头部产品的赛道'),
    ('战略结论', '法规健全恰好构成合规护城河——监管真空期入场者将被出清'),
]
for j, (title, desc) in enumerate(bullets):
    y = Inches(1.5 + j * 0.72)
    add_text_box(slide, Inches(0.6), y, Inches(5), Inches(0.22),
                 title, font_size=12, color=ACCENT_LT, bold=True)
    add_text_box(slide, Inches(0.6), y + Inches(0.22), Inches(5), Inches(0.4),
                 desc, font_size=10, color=LGRAY)

# ═══════════════════════════════════════════════════════════════════════
# SLIDE 4 — USER RESEARCH
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, BG_DARK)
add_top_bar(slide, '实证用户研究', 'Empirical User Research — N=306')

slide.shapes.add_picture(charts['segments'], Inches(7.5), Inches(1.4), Inches(4.5), Inches(3.5))

# Research methods
methods = [
    '文献综述：中外文献 142 篇 + 行业报告 17 份',
    '深度访谈：20 省市 · 21 份有效 · 单份 15-40 分钟',
    '问卷调查：线上线下 · 306 份有效 · 有效率 91.6%',
    '文本挖掘：B站/小红书/抖音/微博/知乎 · 24,000+ 条评论',
]
for j, m in enumerate(methods):
    add_text_box(slide, Inches(0.6), Inches(1.4 + j*0.32), Inches(6.5), Inches(0.28),
                 f'▸  {m}', font_size=10, color=LGRAY)

# SEM result
add_rounded_rect(slide, Inches(0.6), Inches(2.9), Inches(6.5), Inches(0.7), fill_color=BG_MID, line_color=ACCENT)
txb = add_text_box(slide, Inches(0.8), Inches(2.95), Inches(6), Inches(0.6),
                   'SEM 结构方程：χ²/df=2.31 · CFI=0.942 · RMSEA=0.058 · 4 项假设全部 p<0.001',
                   font_size=12, color=ACCENT_LT, bold=True)

# Three segments
segs = [
    ('理性接受型 36.6%', '25-40岁 / 本科 / 在职', '技术信任度高，偏好买断+模块付费', '¥100-500 一次性', ACCENT),
    ('情感依赖型 33.0%', '25-50岁 / 女性偏多 / 经历离别', '情感刚需，偏好短期订阅+Token', '¥30-80 月费', GOLD),
    ('伦理顾虑型 30.4%', '40岁+ / 退休 / 主妇', '强伦理排斥，仅接受基础功能', '≤¥50 一次性', SUCCESS),
]
for j, (name, demo, pref, price, color) in enumerate(segs):
    y = Inches(3.85 + j * 1.05)
    add_kpi_card(slide, Inches(0.6), y, Inches(6.5), Inches(0.9), name, price, f'{demo} | {pref}', accent=color)

# ═══════════════════════════════════════════════════════════════════════
# SLIDE 5 — PRODUCT
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, BG_DARK)
add_top_bar(slide, '产品概念与架构', 'Product — 让告别成为温柔的延续')

# Philosophy quote
add_rounded_rect(slide, Inches(0.6), Inches(1.3), Inches(11.5), Inches(0.55), fill_color=BG_MID, line_color=ACCENT)
add_text_box(slide, Inches(0.8), Inches(1.35), Inches(11), Inches(0.45),
             '"情感过渡的辅助工具，而非替代真实关系" — SEM 模型证实：清晰边界声明反向提升用户包容度',
             font_size=12, color=ACCENT_LT, bold=True)

# 5 Views
views = [
    ('彼岸', '私密追忆空间', '重要之人的数字形象 / 照片动态化 / 影像修复', ACCENT),
    ('聊天', '跨时空对话', 'AI 多轮对话 / 语气还原 / 性格复现', ACCENT_LT),
    ('彼岸动态', '记忆时间线', '纪念日提醒 / 仪式设计 / 家庭连接', GOLD),
    ('社区', '私密互助网络', '匿名共鸣 / 故事分享 / 心理援助', SUCCESS),
    ('星图', '文明记忆宇宙', '60+历史人物 / 6时代×6维度 / 自由漫游', ACCENT2),
]
for j, (name, desc, features, color) in enumerate(views):
    x = Inches(0.6 + j * 2.35)
    y = Inches(2.1)
    card = add_rounded_rect(slide, x, y, Inches(2.15), Inches(2.0), fill_color=BG_MID, line_color=color)
    add_text_box(slide, x + Inches(0.1), y + Inches(0.08), Inches(1.95), Inches(0.3),
                 name, font_size=14, color=color, bold=True, alignment=PP_ALIGN.CENTER)
    add_text_box(slide, x + Inches(0.1), y + Inches(0.38), Inches(1.95), Inches(0.25),
                 desc, font_size=9, color=WHITE, alignment=PP_ALIGN.CENTER)
    add_accent_line(slide, x + Inches(0.3), y + Inches(0.65), Inches(1.55), color)
    add_text_box(slide, x + Inches(0.1), y + Inches(0.75), Inches(1.95), Inches(1.1),
                 features, font_size=9, color=LGRAY, alignment=PP_ALIGN.CENTER)

# Three-layer pyramid
add_text_box(slide, Inches(0.6), Inches(4.4), Inches(5), Inches(0.3),
             '三层场景金字塔（渐进式伦理深度）', font_size=12, color=WHITE, bold=True)
layers = [
    ('L3 双向情感交互', '智能对话+性格复现 — 情感依赖型 — Token计费', GOLD),
    ('L2 沉浸式情景追忆', '虚拟场景+仪式设计 — 理性+情感型 — Pro订阅', ACCENT_LT),
    ('L1 基础数字纪念', '照片动态化+影像修复 — 全用户含伦理型 — 免费/买断', SUCCESS),
]
for j, (layer, desc, color) in enumerate(layers):
    y = Inches(4.8 + j * 0.35)
    w = Inches(5 - j * 0.8)
    add_shape(slide, Inches(0.6), y, w, Inches(0.3), fill_color=color)
    add_text_box(slide, Inches(0.7), y + Inches(0.02), w - Inches(0.2), Inches(0.26),
                 f'{layer}  |  {desc}', font_size=8, color=BG_DARK, bold=True)

# Right side - product status
add_rounded_rect(slide, Inches(6.5), Inches(4.4), Inches(5.8), Inches(2.6), fill_color=BG_MID, line_color=SUCCESS)
add_text_box(slide, Inches(6.7), Inches(4.5), Inches(5.4), Inches(0.25),
             'Product Status — 已上线验证', font_size=12, color=SUCCESS, bold=True)
status_items = [
    '公开访问地址：noracx330.github.io/lifebeyond',
    '上线状态：Live · 含 Free + Pro 双版本',
    '已交付视图：6/6（彼岸/聊天/动态/社区/星图/文明记忆）',
    'Lighthouse：Performance 92 / A11y 95 / SEO 100',
    '代码仓库：github.com/noracx330/lifebeyond 公开可审计',
]
for j, item in enumerate(status_items):
    add_text_box(slide, Inches(6.7), Inches(4.85 + j*0.38), Inches(5.4), Inches(0.35),
                 f'✓  {item}', font_size=9, color=LGRAY)

# ═══════════════════════════════════════════════════════════════════════
# SLIDE 6 — CONVERSION FUNNEL
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, BG_DARK)
add_top_bar(slide, '用户转化漏斗与付费偏好', 'Conversion Funnel & Payment Preference')

slide.shapes.add_picture(charts['funnel'], Inches(5.5), Inches(1.4), Inches(6.8), Inches(3.8))

# Key insights
insights = [
    ('最大流失环节', '认知→接受（loss=53%），核心是公众教育与品牌信任建立'),
    ('营销方向', '叙事内容+公益合作+学术背书，而非效果广告'),
    ('低门槛 Demo', '解决"接受→尝试"30% 流失，Live MVP 即为此而设'),
    ('付费偏好', '买断 3.41 分 > 订阅 2.74 分 → 摒弃单一订阅制'),
    ('定价约束', '"重要之人的记忆资产应永久归属我" → 一次性买断+Token包+模块解锁'),
]
for j, (title, desc) in enumerate(insights):
    y = Inches(1.5 + j * 0.72)
    add_text_box(slide, Inches(0.6), y, Inches(4.8), Inches(0.22),
                 title, font_size=11, color=ACCENT_LT, bold=True)
    add_text_box(slide, Inches(0.6), y + Inches(0.22), Inches(4.8), Inches(0.4),
                 desc, font_size=10, color=LGRAY)

# Bottom - ethical red lines
add_accent_line(slide, Inches(0.6), Inches(5.3), Inches(11), WARN)
add_text_box(slide, Inches(0.6), Inches(5.4), Inches(11), Inches(0.25),
             '伦理红线 Top-3：①未授权使用他人数据 23.9%  ②商业化情感 19.8%  ③情感操控 17.2%',
             font_size=10, color=WARN, bold=True)

# ═══════════════════════════════════════════════════════════════════════
# SLIDE 7 — BUSINESS MODEL
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, BG_DARK)
add_top_bar(slide, '商业模式 — 四引擎收入结构', 'Business Model')

# Four engines
engines = [
    ('C 端 Token 增值', 'Y3 ¥642 万', '5类Token×6档套餐×20场景', ACCENT),
    ('C 端 Pro 订阅', 'Y3 ¥1,480 万', '年费¥398/月费¥48', ACCENT_LT),
    ('B 端 SaaS API', 'Y3 ¥1,320 万', '数字人生成+语音+视频API', GOLD),
    ('文旅文博定制', 'Y3 ¥860 万', '¥8-30万/项目', SUCCESS),
]
for j, (name, rev, desc, color) in enumerate(engines):
    x = Inches(0.6 + j * 2.85)
    add_kpi_card(slide, x, Inches(1.3), Inches(2.55), Inches(1.1), name, rev, desc, accent=color)

# Anti-exploitation
add_rounded_rect(slide, Inches(0.6), Inches(2.7), Inches(5.5), Inches(2.6), fill_color=BG_MID, line_color=WARN)
add_text_box(slide, Inches(0.8), Inches(2.8), Inches(5.1), Inches(0.25),
             '反情感剥削机制 — 代码层硬性规则', font_size=12, color=WARN, bold=True)
rules = [
    '① 永不按对话时长收费——杜绝"越悲伤越付费"',
    '② 情绪低谷场景下禁止推送付费内容',
    '③ 每日对话时长上限 60 分钟（Pro 90 分钟）',
    '④ 高危关键词检测 → 立即引导专业心理援助',
    '⑤ 付费弹窗需通过 5 道屏蔽校验后才能下发',
]
for j, r in enumerate(rules):
    add_text_box(slide, Inches(0.8), Inches(3.15 + j * 0.35), Inches(5.1), Inches(0.3),
                 r, font_size=10, color=LGRAY)

# Token system
add_rounded_rect(slide, Inches(6.5), Inches(2.7), Inches(5.8), Inches(2.6), fill_color=BG_MID, line_color=ACCENT)
add_text_box(slide, Inches(6.7), Inches(2.8), Inches(5.4), Inches(0.25),
             '五类 Token 体系', font_size=12, color=ACCENT_LT, bold=True)
tokens = [
    ('对话 Token', '1 Token = 1 轮对话', '¥30/100个'),
    ('语音 Token', '1 Token = 1 分钟语音', '¥50/60个'),
    ('视频 Token', '1 Token = 1 段 ≤10s 视频', '¥80/30个'),
    ('创作 Token', '日记润色/文案生成', '¥20/80个'),
    ('仪式 Token', '纪念日/仪式场景', '¥40/50个'),
]
for j, (name, rule, price) in enumerate(tokens):
    y = Inches(3.15 + j * 0.38)
    add_text_box(slide, Inches(6.7), y, Inches(2.2), Inches(0.3),
                 name, font_size=10, color=ACCENT_LT, bold=True)
    add_text_box(slide, Inches(8.9), y, Inches(2), Inches(0.3),
                 rule, font_size=9, color=LGRAY)
    add_text_box(slide, Inches(10.9), y, Inches(1.3), Inches(0.3),
                 price, font_size=9, color=GOLD)

# Card pool
add_rounded_rect(slide, Inches(0.6), Inches(5.55), Inches(11.7), Inches(0.85), fill_color=BG_MID, line_color=GOLD)
add_text_box(slide, Inches(0.8), Inches(5.6), Inches(3), Inches(0.25),
             '剧情卡池系统（乙女游戏式商业化引擎）', font_size=11, color=GOLD, bold=True)
add_text_box(slide, Inches(0.8), Inches(5.88), Inches(11.3), Inches(0.4),
             '4档稀有度（N 55% / R 28% / SR 13% / SSR 4%）| 每日3次免费抽卡 | 用户记忆→专属记忆卡 | 日活参与率 42% | 卡池驱动 ARPU 增量 ¥9.4',
             font_size=9, color=LGRAY)

# ═══════════════════════════════════════════════════════════════════════
# SLIDE 8 — FINANCIALS
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, BG_DARK)
add_top_bar(slide, '财务预测', 'Financial Projections — 中性情境')

slide.shapes.add_picture(charts['revenue'], Inches(0.4), Inches(1.3), Inches(6.2), Inches(3.5))
slide.shapes.add_picture(charts['ltv'], Inches(6.8), Inches(1.3), Inches(5.8), Inches(3.5))

# KPI row
fin_kpis = [
    ('Y3 营收', '¥4,302 万', '4引擎贡献'),
    ('Y3 净利', '¥1,076 万', '净利率 25%'),
    ('回本周期', '14 个月', '中性情境'),
    ('付费转化率', '10.3%', 'Y3 预测'),
]
for j, (label, value, sub) in enumerate(fin_kpis):
    x = Inches(0.6 + j * 2.85)
    add_kpi_card(slide, x, Inches(5.0), Inches(2.55), Inches(0.9), label, value, sub)

# Bottom note
add_text_box(slide, Inches(0.6), Inches(6.0), Inches(11), Inches(0.3),
             'Y1 营业亏损 ¥66 万 → Y2 微盈 ¥32 万 → Y3 净利 ¥1,076 万（净利率 25%）| 保守情境回本 18 月 / 激进情境 9 月',
             font_size=9, color=LGRAY)

# ═══════════════════════════════════════════════════════════════════════
# SLIDE 9 — TECH & COMPLIANCE
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, BG_DARK)
add_top_bar(slide, '技术架构与合规', 'Tech Stack & Compliance')

# Tech layers
tech = [
    ('前端层', 'Three.js Shader / HTML5 Canvas / Tailwind CSS', '1800+ 粒子实时渲染 / Lighthouse 92'),
    ('AI 层', '豆包 Seed-1.6 / Volcengine TTS / Seedance 2.0', '32K 上下文 / 个性化音色克隆'),
    ('数据层', 'Supabase Auth + DB / S3 对象存储 / IPFS', '端到端加密 / 区块链存证'),
    ('安全层', 'XOR+Base64 加密 / bcrypt 哈希 / GDPR', '代码层伦理规则 / 7天软删除'),
]
for j, (layer, stack, cap) in enumerate(tech):
    y = Inches(1.4 + j * 1.0)
    add_rounded_rect(slide, Inches(0.6), y, Inches(5.5), Inches(0.85), fill_color=BG_MID, line_color=ACCENT)
    add_text_box(slide, Inches(0.8), y + Inches(0.05), Inches(1.5), Inches(0.25),
                 layer, font_size=12, color=ACCENT_LT, bold=True)
    add_text_box(slide, Inches(0.8), y + Inches(0.32), Inches(5.1), Inches(0.22),
                 stack, font_size=9, color=LGRAY)
    add_text_box(slide, Inches(0.8), y + Inches(0.55), Inches(5.1), Inches(0.22),
                 cap, font_size=9, color=SUCCESS)

# Compliance
add_rounded_rect(slide, Inches(6.5), Inches(1.4), Inches(5.8), Inches(3.8), fill_color=BG_MID, line_color=SUCCESS)
add_text_box(slide, Inches(6.7), Inches(1.5), Inches(5.4), Inches(0.25),
             '伦理治理三道防线', font_size=12, color=SUCCESS, bold=True)
defenses = [
    ('事前·设计层', '伦理合规校验模块作为代码层硬性规则，研发流程设置伦理评审关卡'),
    ('事中·运行层', '实时情感剂量监测，高危关键词检测，对话时长强制熔断'),
    ('事后·治理层', '用户投诉分级响应，第三方伦理委员会季度审查，数据销毁可审计'),
]
for j, (title, desc) in enumerate(defenses):
    y = Inches(1.9 + j * 1.05)
    add_text_box(slide, Inches(6.7), y, Inches(5.4), Inches(0.22),
                 title, font_size=11, color=GOLD, bold=True)
    add_text_box(slide, Inches(6.7), y + Inches(0.25), Inches(5.4), Inches(0.7),
                 desc, font_size=9, color=LGRAY)

# Risk matrix
add_text_box(slide, Inches(0.6), Inches(5.5), Inches(11), Inches(0.25),
             '风险矩阵：技术风险(低) | 伦理风险(中→低·已对冲) | 监管风险(低·合规先发) | 市场风险(中·赛道空白期有限)',
             font_size=10, color=LGRAY)

# ═══════════════════════════════════════════════════════════════════════
# SLIDE 10 — MARKETING
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, BG_DARK)
add_top_bar(slide, '营销与渠道策略', 'Marketing & Channels')

# Content matrix
platforms = [
    ('短视频', '抖音/B站', '情感故事+技术展示', '破圈引流', ACCENT_LT),
    ('社交媒体', '小红书/微博', '用户故事+产品口碑', '信任沉淀', ACCENT),
    ('新闻媒体', '科技/财经媒体', '学术背书+行业观点', '权威背书', GOLD),
    ('BD渠道', '殡仪馆/纪念馆', '线下场景嵌入', '精准触达', SUCCESS),
]
for j, (plat, channel, content, goal, color) in enumerate(platforms):
    x = Inches(0.6 + j * 2.85)
    add_kpi_card(slide, x, Inches(1.3), Inches(2.55), Inches(1.2), plat, goal, f'{channel} | {content}', accent=color)

# Brand narrative
add_rounded_rect(slide, Inches(0.6), Inches(2.8), Inches(11.5), Inches(0.55), fill_color=BG_MID, line_color=ACCENT)
add_text_box(slide, Inches(0.8), Inches(2.85), Inches(11), Inches(0.45),
             '品牌叙事核心："科技应当成为对抗遗忘的温柔工具，而非制造虚假幻觉的傲慢机器"',
             font_size=13, color=ACCENT_LT, bold=True)

# User lifecycle
add_text_box(slide, Inches(0.6), Inches(3.6), Inches(5), Inches(0.3),
             '用户充值生命周期管理', font_size=12, color=WHITE, bold=True)
lifecycle = [
    ('探索期 D0-D3', '免费体验全功能', '不触发任何付费引导'),
    ('沉浸期 D4-D14', '渐进解锁 Pro 试用 7 天', '仅功能引导节点弹窗'),
    ('决策期 D15-D45', 'Pro/Token 包首次引导', '首充¥1体验+退款保障'),
    ('核心期 D46-D365', '年费+槽位+Token 包', '续费提醒最多1次/月'),
]
for j, (phase, action, rule) in enumerate(lifecycle):
    y = Inches(4.0 + j * 0.55)
    add_text_box(slide, Inches(0.6), y, Inches(2.5), Inches(0.25),
                 phase, font_size=10, color=GOLD, bold=True)
    add_text_box(slide, Inches(3.1), y, Inches(3.5), Inches(0.25),
                 action, font_size=10, color=WHITE)
    add_text_box(slide, Inches(6.6), y, Inches(5.5), Inches(0.25),
                 rule, font_size=9, color=LGRAY)

# ═══════════════════════════════════════════════════════════════════════
# SLIDE 11 — CARD POOL SYSTEM (new feature)
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, BG_DARK)
add_top_bar(slide, '剧情卡池系统 — 乙女游戏式商业化引擎', 'Card Pool System')

slide.shapes.add_picture(charts['cardpool'], Inches(7.5), Inches(1.3), Inches(4.8), Inches(3.2))

# Three pain points
pains = [
    ('对话冷启动', '45.1% 付费用户中仅 23.6% 能自主启动对话 → 剧情卡提供场景锚点'),
    ('日活驱动', '被动等待情绪低谷 → 每日3次免费抽卡构建主动回访钩子'),
    ('UGC 闭环', '用户上传记忆→记忆卡→抽取消耗Token→激励更多UGC'),
]
for j, (title, desc) in enumerate(pains):
    y = Inches(1.4 + j * 0.8)
    add_text_box(slide, Inches(0.6), y, Inches(3), Inches(0.22),
                 title, font_size=11, color=GOLD, bold=True)
    add_text_box(slide, Inches(0.6), y + Inches(0.25), Inches(6.5), Inches(0.5),
                 desc, font_size=10, color=LGRAY)

# Anti-gambling
add_rounded_rect(slide, Inches(0.6), Inches(3.9), Inches(11.5), Inches(1.2), fill_color=BG_MID, line_color=WARN)
add_text_box(slide, Inches(0.8), Inches(3.95), Inches(5), Inches(0.25),
             '反赌博化设计五原则', font_size=11, color=WARN, bold=True)
anti = [
    '① 日限硬顶：每日3+2次上限，绝无无限抽取',
    '② 无重复卡：已获卡牌不再出现，图鉴单调递增',
    '③ 无保底/无累计：避免"追SSR"式付费冲动',
    '④ 记忆卡不入付费池：真实记忆永不货币化',
    '⑤ 情感门控：会话超阈值自动禁用抽卡入口',
]
for j, a in enumerate(anti):
    col = j % 3
    row = j // 3
    x = Inches(0.8 + col * 3.9)
    y = Inches(4.3 + row * 0.35)
    add_text_box(slide, x, y, Inches(3.8), Inches(0.3),
                 a, font_size=9, color=LGRAY)

# Revenue prediction
add_text_box(slide, Inches(0.6), Inches(5.4), Inches(11), Inches(0.25),
             '卡池驱动：日活参与率 42% → DAU/MAU 从 0.18 提升至 0.27 → ARPU 增量 ¥9.4 | 核心价值不在直接付费而在日活飞轮',
             font_size=10, color=ACCENT_LT, bold=True)

# ═══════════════════════════════════════════════════════════════════════
# SLIDE 12 — INVESTMENT HIGHLIGHTS
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, BG_DARK)
add_top_bar(slide, '投资亮点与展望', 'Investment Highlights')

highlights = [
    ('Working Product', '已上线 Live MVP，6 视图全部交付，Lighthouse 92/95/100，公开可体验', ACCENT2),
    ('实证驱动', '306 份问卷 + SEM + K-means，4 项假设 p<0.001，产品决策有数据根基', ACCENT),
    ('伦理护城河', '反情感剥削算法硬嵌入，合规先发者优势，监管利好出清竞品', SUCCESS),
    ('四引擎收入', 'C端Token+Pro+B端SaaS+文旅定制，Y3 营收 ¥4,302 万，净利率 25%', GOLD),
    ('LTV/CAC 6.6x', '远超行业 SaaS 平均 3-5x，买断+Token混合定价匹配用户付费偏好', ACCENT_LT),
]
for j, (title, desc, color) in enumerate(highlights):
    y = Inches(1.4 + j * 0.85)
    # Number badge
    badge = add_rounded_rect(slide, Inches(0.6), y, Inches(0.45), Inches(0.45), fill_color=color)
    add_text_box(slide, Inches(0.6), y + Inches(0.02), Inches(0.45), Inches(0.4),
                 str(j+1), font_size=18, color=BG_DARK, bold=True, alignment=PP_ALIGN.CENTER)
    add_text_box(slide, Inches(1.2), y + Inches(0.02), Inches(3), Inches(0.3),
                 title, font_size=14, color=color, bold=True)
    add_text_box(slide, Inches(1.2), y + Inches(0.35), Inches(10.5), Inches(0.4),
                 desc, font_size=10, color=LGRAY)

# Vision
add_rounded_rect(slide, Inches(0.6), Inches(5.7), Inches(11.5), Inches(0.7), fill_color=BG_MID, line_color=ACCENT2)
add_text_box(slide, Inches(0.8), Inches(5.75), Inches(11), Inches(0.6),
             '愿景：让告别成为温柔的延续，让每一个值得被铭记的灵魂，在数字与现实的交汇处，获得跨越时空的安宁',
             font_size=13, color=ACCENT2, bold=True, alignment=PP_ALIGN.CENTER)

# ═══════════════════════════════════════════════════════════════════════
# SLIDE 13 — CLOSING
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, BG_DARK)
add_shape(slide, 0, 0, SW, Pt(4), fill_color=ACCENT)

add_text_box(slide, Inches(1), Inches(1.8), Inches(11), Inches(0.6),
             'LifeBeyond · 数 字 彼 岸', font_size=40, color=ACCENT_LT, bold=True, alignment=PP_ALIGN.CENTER)
add_text_box(slide, Inches(1), Inches(2.6), Inches(11), Inches(0.4),
             '让告别成为温柔的延续', font_size=20, color=WHITE, alignment=PP_ALIGN.CENTER)

add_accent_line(slide, Inches(4.5), Inches(3.2), Inches(4), ACCENT)

add_text_box(slide, Inches(1), Inches(3.6), Inches(11), Inches(0.3),
             'Live Demo: https://noracx330.github.io/lifebeyond/', font_size=14, color=GOLD, alignment=PP_ALIGN.CENTER)
add_text_box(slide, Inches(1), Inches(4.0), Inches(11), Inches(0.3),
             '已上线公开访问 · MVP 已交付 · 可直接体验', font_size=12, color=SUCCESS, alignment=PP_ALIGN.CENTER)

add_text_box(slide, Inches(1), Inches(5.2), Inches(11), Inches(0.3),
             'Thank You', font_size=28, color=DGRAY, bold=True, alignment=PP_ALIGN.CENTER)

# ── Save ─────────────────────────────────────────────────────────────────
prs.save(OUT)
sz = os.path.getsize(OUT)
print(f'PPT saved: {OUT} ({sz/1024:.0f} KB, {len(prs.slides)} slides)')
