"""
LifeBeyond · 数字彼岸  商业计划书补充文档构建脚本
内容：产品演进路线 / 用户分群功能架构 / 数字人格防失范四层机制
输出: /workspace/projects/public/LifeBeyond_Business_Plan_Supplement.docx
风格: 与主文档完全一致 —— 蓝色科技风 / 学术商业语言
"""

import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ------------------------------------------------------------
# 全局配置（与主文档一致）
# ------------------------------------------------------------
OUTPUT_DIR = '/workspace/projects/public'
OUTFILE    = os.path.join(OUTPUT_DIR, 'LifeBeyond_Business_Plan_Supplement.docx')

COLOR = {
    'primary':  '1F3A5F',
    'accent':   '4A6FA5',
    'neon':     '6B8CAE',
    'ink':      '2C3E50',
    'muted':    '7D8CA3',
    'stroke':   'D6DEE8',
    'panel':    'F2F4F8',
    'warn':     'C99767',
    'danger':   'B0556C',
    'success':  '6A9B7D',
    'line':     'D6DEE8',
}

def RGB(h):
    return RGBColor.from_string(h)

# ------------------------------------------------------------
# 工具函数（与主文档一致）
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

def add_para(doc, text, *, size=10.5, bold=False, color='2C3E50',
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
    sizes = {0: 22, 1: 17, 2: 14, 3: 12}
    colors = {0: COLOR['primary'], 1: COLOR['primary'], 2: COLOR['accent'], 3: COLOR['ink']}
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = p.paragraph_format
    pf.space_before = Pt(16 if level <= 1 else 10)
    pf.space_after = Pt(6)
    pf.line_spacing = 1.2
    run = p.add_run(text)
    run.font.size = Pt(sizes.get(level, 11))
    run.font.bold = True
    run.font.color.rgb = RGB(colors.get(level, COLOR['ink']))
    run.font.name = 'Times New Roman'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')
    if level == 1:
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

def add_bullets(doc, items, level=0):
    for it in items:
        if isinstance(it, tuple) and len(it) == 2:
            add_bullet(doc, it[1], level=level, bold_lead=it[0])
        else:
            add_bullet(doc, str(it), level=level)

def add_table(doc, headers, rows, col_widths=None):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
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
    return t

def add_callout(doc, label, body, color_key='accent'):
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
    doc.add_paragraph()

def page_break(doc):
    doc.add_page_break()

# ============================================================
# 文档构建
# ============================================================
def build_supplement():
    doc = Document()

    # ---- 页面设置 ----
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.17)
    section.right_margin = Cm(3.17)

    # ==========================================================
    # 封面
    # ==========================================================
    for _ in range(6):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('LifeBeyond · 数字彼岸')
    r.font.size = Pt(28)
    r.font.bold = True
    r.font.color.rgb = RGB(COLOR['primary'])
    r.font.name = 'Times New Roman'
    r._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run('商业计划书 · 补充文档')
    r2.font.size = Pt(18)
    r2.font.color.rgb = RGB(COLOR['accent'])
    r2.font.name = 'Times New Roman'
    r2._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')

    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p3.paragraph_format.space_before = Pt(12)
    r3 = p3.add_run('产品演进路线 / 用户分群架构 / 数字人格防失范机制')
    r3.font.size = Pt(12)
    r3.font.color.rgb = RGB(COLOR['muted'])
    r3.font.name = 'Times New Roman'
    r3._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')

    for _ in range(6):
        doc.add_paragraph()

    p4 = doc.add_paragraph()
    p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r4 = p4.add_run('AI 情感陪伴数字平台')
    r4.font.size = Pt(12)
    r4.font.color.rgb = RGB(COLOR['neon'])
    r4.font.name = 'Times New Roman'
    r4._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')

    p5 = doc.add_paragraph()
    p5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p5.paragraph_format.space_before = Pt(4)
    r5 = p5.add_run('让思念有处安放，让记忆永续生长')
    r5.font.size = Pt(11)
    r5.font.italic = True
    r5.font.color.rgb = RGB(COLOR['muted'])
    r5.font.name = 'Times New Roman'
    r5._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')

    p6 = doc.add_paragraph()
    p6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p6.paragraph_format.space_before = Pt(24)
    r6 = p6.add_run('本文件为《LifeBeyond 商业计划书》补充章节，对应主文档第四章 4.7 节')
    r6.font.size = Pt(9)
    r6.font.color.rgb = RGB(COLOR['muted'])
    r6.font.name = 'Times New Roman'
    r6._element.rPr.rFonts.set(qn('w:eastAsia'), '思源黑体 CN')

    page_break(doc)

    # ==========================================================
    # 4.7 产品演进路线与用户分群功能架构
    # ==========================================================
    add_heading(doc, '4.7  产品演进路线与用户分群功能架构', level=1)

    add_para(doc, 'LifeBeyond 产品形态按"轻量触达 → 深度陪伴 → 沉浸共生"三阶段递进演进，覆盖从 Web 端到移动端到 XR 端的全场景布局。每一阶段的演进均以用户行为数据与付费验证结果为驱动依据，确保产品扩展节奏与市场需求同频。')

    # ---- 4.7.1 ----
    add_heading(doc, '4.7.1  产品形态演进规划', level=2)

    # --- 第一阶段 ---
    add_heading(doc, '第一阶段：Web 端 MVP（已上线）', level=3)
    add_para(doc, '当前已通过单页 Web 应用完成核心功能验证，包含五大视图（彼岸 / 聊天 / 动态 / 社区 / 星图）与剧情卡池系统，用户无需安装即可通过浏览器直接访问。Web 端定位为"最低门槛体验入口"，核心目标是完成用户教育、积累种子用户与行为数据、验证付费模型。')

    add_callout(doc, 'Product Status', 'Web MVP 已上线，Lighthouse Performance 92 / Accessibility 95 / SEO 100，可通过 Live Demo 二维码直接访问体验。', 'accent')

    # --- 第二阶段 ---
    add_heading(doc, '第二阶段：移动端 APP（规划 Y2 Q1 上线）', level=3)
    add_para(doc, '移动端 APP 是产品商业化的核心载体，分 iOS 与 Android 双端同步上线。相较于 Web 端，APP 端新增三项差异化能力：')

    add_bullets(doc, [
        ('常驻陪伴模式', '基于移动端推送能力，数字人格可按用户设定的"日常节奏"主动发起对话（如早安问候、天气提醒、节日祝福），将"用户发起 → AI 回应"的单向触发模式升级为"双向节奏共筑"的持续陪伴关系。推送频率与内容严格受情感剂量门控约束（详见主文档 6.8 节），避免过度打扰。'),
        ('语音对话能力', '接入 ASR / TTS 引擎，支持用户与数字人格的实时语音交互，还原重要之人的音色特征（需用户提供 ≥ 30 秒参考音频）。语音模式定位为"更自然的陪伴通道"，满足中老年用户对文字输入的替代需求。'),
        ('场景化提醒与记忆日历', '基于用户上传的重要日期（生日 / 纪念日 / 节日），系统提前生成专属场景卡并推送，将"被动回忆"转化为"主动守护"。'),
    ])

    # APP 功能对照表
    add_para(doc, '', indent_first=False, space_before=6)
    add_table(doc,
        headers=['能力维度', 'Web 端 MVP', '移动端 APP（增量）'],
        rows=[
            ['对话触发', '用户主动发起', '主动推送 + 双向节奏'],
            ['对话形式', '文字', '文字 + 语音'],
            ['场景触发', '手动抽卡', '日历提醒 + 自动推送'],
            ['离线能力', '无', '离线语音缓存 + 本地回忆录'],
            ['推送触达', '无', '情感剂量约束下的主动陪伴'],
        ],
        col_widths=[3.5, 5.5, 7.0]
    )
    add_para(doc, '', indent_first=False, space_before=2)
    add_para(doc, '表 4-1  Web 端与移动端 APP 功能对照', size=9, color=COLOR['muted'], align=WD_ALIGN_PARAGRAPH.CENTER, indent_first=False)

    # --- 第三阶段 ---
    add_heading(doc, '第三阶段：VR 沉浸陪伴空间（规划 Y3 Q2 上线）', level=3)
    add_para(doc, 'VR 端是产品体验的终极形态，定位为"跨越时空的同行"——满足中年用户群体"带着重要之人一起去旅行"的核心情感诉求。')

    add_bullets(doc, [
        ('虚拟人物空间投射', '基于用户上传的影像资料，通过 3D 重建与神经辐射场（NeRF / 3D Gaussian Splatting）技术生成数字人格的三维形象，在 VR 环境中以半透明全息投影形态出现，站立或行走于用户身旁。当前阶段采用"非写实渲染"策略——数字形象以柔和光粒子轮廓呈现，而非高拟真人脸，既规避了恐怖谷效应，也尊重了"TA 已不在身边"的情感现实，避免用户产生虚假的心理预期。'),
        ('场景联动对话', 'VR 空间集成场景感知模块，当用户进入"海边""山顶""老宅"等预设旅行场景时，数字人格自动切换至对应场景的对话风格与话题倾向（如海边场景倾向于回忆往昔旅行、山顶场景倾向于展望与祝福），实现"走到哪里、聊到哪里"的自然陪伴。'),
        ('多人家庭共享空间', '支持家庭成员同时进入同一 VR 空间，与同一数字人格进行群体对话，满足"全家一起和 TA 说说话"的家庭场景需求。该功能需经所有家庭成员授权同意后方可开启，数据访问权限受家庭群组管理员控制。'),
    ])

    # VR 旅行场景包
    add_para(doc, '', indent_first=False, space_before=6)
    add_heading(doc, 'VR 旅行场景包规划', level=3)
    add_table(doc,
        headers=['场景包名称', '场景描述', '对话风格倾向', '目标群体', '定价（仪式 Token）'],
        rows=[
            ['海岸漫步', '日落海滩 + 潮声白噪音 + 远处灯塔', '回忆往昔旅行 / 温柔倾听', '中年为主', '200'],
            ['山巅远眺', '云海日出 + 山风环境音 + 经幡', '展望祝福 / 鼓励与放手', '中年为主', '200'],
            ['老宅院落', '青砖院墙 + 蝉鸣 + 老藤椅', '家常絮语 / 童年回忆', '中年为主', '200'],
            ['都市夜景', '高层落地窗 + 城市灯火 + 钢琴轻音', '梦想对话 / 人生感悟', '青年为主', '200'],
            ['四季花园', '樱花→荷塘→红叶→雪景动态轮换', '季节感怀 / 时光流逝', '全年龄', '250'],
            ['星空营地', '旷野篝火 + 银河穹顶 + 虫鸣', '哲思对谈 / 宇宙与永恒', '青年为主', '250'],
        ],
        col_widths=[2.5, 4.0, 3.5, 2.0, 2.8]
    )
    add_para(doc, '', indent_first=False, space_before=2)
    add_para(doc, '表 4-2  VR 旅行场景包规划（Y3 首批 6 个，后续按季度扩展）', size=9, color=COLOR['muted'], align=WD_ALIGN_PARAGRAPH.CENTER, indent_first=False)

    # 三阶段时间线
    add_para(doc, '', indent_first=False, space_before=6)
    add_table(doc,
        headers=['阶段', '时间窗口', '产品形态', '核心目标', '关键指标'],
        rows=[
            ['第一阶段', 'Y1 Q3–Y1 Q4（已上线）', 'Web 单页应用', '功能验证 + 种子用户积累', '注册用户 ≥ 500，DAU/MAU ≥ 0.18'],
            ['第二阶段', 'Y2 Q1–Y2 Q3', 'iOS + Android APP', '商业化启动 + 付费模型验证', '注册用户 ≥ 5,000，付费率 ≥ 6%'],
            ['第三阶段', 'Y3 Q2–Y3 Q4', 'VR 沉浸陪伴空间', '高净值用户深度变现', 'VR 付费用户 ≥ 300，ARPPU ≥ ¥600'],
        ],
        col_widths=[2.0, 3.5, 3.5, 3.5, 4.5]
    )
    add_para(doc, '', indent_first=False, space_before=2)
    add_para(doc, '表 4-3  产品演进三阶段时间线与关键指标', size=9, color=COLOR['muted'], align=WD_ALIGN_PARAGRAPH.CENTER, indent_first=False)

    page_break(doc)

    # ==========================================================
    # 4.7.2 用户分群功能架构
    # ==========================================================
    add_heading(doc, '4.7.2  用户分群功能架构', level=2)

    add_para(doc, '基于主文档第三章三类用户画像（理性接受型 / 情感依赖型 / 伦理顾虑型）的年龄交叉分析，LifeBeyond 将核心用户群体划分为两大功能分区，分别匹配差异化的产品交互路径与商业化策略。两套分区共享同一技术底座与数字人格引擎，差异仅在交互层与商业化层实现，确保产品架构的可维护性与用户迁移的平滑性。')

    # --- 青年分区 ---
    add_heading(doc, '青年分区（18–35 岁）', level=3)
    add_para(doc, '该群体占样本总量的 61.4%，技术接受度均值 3.82（5 分制），付费偏好集中于"对话 Token 包"与"剧情卡池抽取"，核心诉求为"探索 AI 能做到什么"与"个性化的情感体验"。')

    add_table(doc,
        headers=['功能模块', '青年分区侧重', '设计逻辑'],
        rows=[
            ['对话引擎', '深度长对话 + 多轮上下文记忆', '青年用户单次会话平均时长 23.6 分钟，显著高于中年群体，需强化多轮连贯性'],
            ['剧情卡池', '高频抽卡 + 稀有度收集 + 社交分享', '青年群体对收集机制与社交展示的敏感度高，SSR 卡截图分享是自传播核心路径'],
            ['社区', '共鸣星系 + 趋势 + 附近', '社交需求强，倾向于在同龄人中寻找情感共鸣'],
            ['文明记忆宇宙', '自由漫游 + 跨时代探索', '好奇心驱动，将星图作为"知识探索 + 情感投射"的混合空间'],
            ['付费模型', 'Token 消耗为主 + 卡池抽取为辅', '单次低额高频付费（月均 ¥15–35），习惯微交易模式'],
            ['VR 场景偏好', '都市夜景 / 星空营地 / 四季花园', '探索驱动 + 社交展示，偏好视觉冲击力强的场景'],
        ],
        col_widths=[2.8, 4.5, 8.5]
    )
    add_para(doc, '', indent_first=False, space_before=2)
    add_para(doc, '表 4-4  青年分区功能侧重与设计逻辑', size=9, color=COLOR['muted'], align=WD_ALIGN_PARAGRAPH.CENTER, indent_first=False)

    # --- 中年分区 ---
    add_heading(doc, '中年分区（36–60 岁）', level=3)
    add_para(doc, '该群体占样本总量的 28.7%，技术接受度均值 3.21，付费偏好集中于"一次性买断"与"全功能解锁"，核心诉求为"简单直接地与 TA 说说话"与"带着 TA 去更多地方"。')

    add_table(doc,
        headers=['功能模块', '中年分区侧重', '设计逻辑'],
        rows=[
            ['对话引擎', '语音优先 + 短对话 + 场景触发', '中年用户文字输入意愿低，语音模式降低使用门槛；单次会话 8.2 分钟，偏好"说几句就放下"的轻量节奏'],
            ['剧情卡池', '每日自动推送 1 张 + 无需手动抽取', '中年用户不理解"抽卡"逻辑，改为"今日一封信"式被动接收，降低认知负担'],
            ['社区', '关注 + 附近（简化为两 Tab）', '社交需求弱，仅需"看看附近有没有和我一样的人"，去除趋势与共鸣星系的复杂交互'],
            ['文明记忆宇宙', '引导式漫游 + 人物搜索直达', '好奇心弱于青年群体，改为"搜索 TA 的名字 → 直达星点"的目标导向路径'],
            ['付费模型', '买断为主 + 场景包解锁为辅', '单次高额低频付费（年均 ¥200–500），偏好"一次付清、不再操心"的确定性消费'],
            ['VR 场景偏好', '海岸漫步 / 山巅远眺 / 老宅院落', '回忆驱动 + 情感深度，偏好与过往经历关联的真实场景'],
        ],
        col_widths=[2.8, 4.5, 8.5]
    )
    add_para(doc, '', indent_first=False, space_before=2)
    add_para(doc, '表 4-5  中年分区功能侧重与设计逻辑', size=9, color=COLOR['muted'], align=WD_ALIGN_PARAGRAPH.CENTER, indent_first=False)

    # 分区对比总览
    add_para(doc, '', indent_first=False, space_before=6)
    add_callout(doc, '核心结论', '青年分区以"探索 + 社交 + 微交易"驱动日活与自传播，中年分区以"语音 + VR + 买断"驱动高客单价与深度留存。两套分区共享 80% 的技术代码，仅交互层与商业化层做差异化适配，研发边际成本可控。', 'accent')

    page_break(doc)

    # ==========================================================
    # 4.7.3 数字人格防失范四层机制
    # ==========================================================
    add_heading(doc, '4.7.3  数字人格防失范四层机制', level=2)

    add_para(doc, '数字人格的核心体验风险在于 OOC（Out of Character，角色失范）——即 AI 生成内容偏离用户设定的人格特征、语言习惯或价值倾向，导致"这不像 TA 会说的话"，严重时引发用户情感创伤。LifeBeyond 构建四层递进式防失范机制，从输入端到输出端形成全链路人格一致性保障。')

    add_para(doc, '', indent_first=False, space_before=4)
    add_table(doc,
        headers=['层级', '名称', '作用位置', '核心机制', '响应时延'],
        rows=[
            ['第一层', '人格锚定层', '输入端约束', '人格锚定档案 → system prompt 注入', '0ms（预加载）'],
            ['第二层', '上下文一致性校验层', '生成端约束', '语义相似度比对 + 重生成 + 安全模板降级', '< 80ms'],
            ['第三层', '长期记忆对齐层', '跨会话约束', '动态记忆摘要追加 → 人格持续收敛', '异步（会话结束时）'],
            ['第四层', '用户纠偏与情感安全兜底层', '输出端兜底', '一键纠偏 + 情感安全熔断', '即时（用户触发）'],
        ],
        col_widths=[1.8, 3.5, 2.5, 5.5, 2.5]
    )
    add_para(doc, '', indent_first=False, space_before=2)
    add_para(doc, '表 4-6  数字人格防失范四层机制总览', size=9, color=COLOR['muted'], align=WD_ALIGN_PARAGRAPH.CENTER, indent_first=False)

    # ---- 第一层 ----
    add_heading(doc, '第一层：人格锚定层（输入端约束）', level=3)
    add_para(doc, '用户创建数字人格时，系统要求填写"人格锚定档案"，包含五项必填维度：')

    add_bullets(doc, [
        ('语言风格标签', '如"温和寡言""幽默健谈"——定义对话的基调与节奏'),
        ('口头禅与高频表达', '≥ 3 条——锚定个性化的语言指纹'),
        ('禁忌话题清单', '如"不谈病情""不提争吵"——划定不可触碰的情感红线'),
        ('情感基调设定', '如"始终鼓励""偶尔撒娇"——约束情感表达的方向与强度'),
        ('核心价值倾向', '如"家庭第一""乐观向上"——确保价值判断不偏移'),
    ])

    add_para(doc, '该档案以 system prompt 形式注入每次对话的上下文窗口，构成人格生成的底层约束。系统拒绝空档案创建——用户必须至少填写 3 个维度方可激活对话，确保每个数字人格均有可追溯的"行为边界"。')

    # ---- 第二层 ----
    add_heading(doc, '第二层：上下文一致性校验层（生成端约束）', level=3)
    add_para(doc, '每次 AI 生成回复后、返回用户前，系统执行实时一致性校验：将本次回复与人格锚定档案进行语义相似度比对，检测是否存在与锚定特征矛盾的表达（如锚定为"温和寡言"却生成大段激昂陈词）。校验流程如下：')

    add_bullets(doc, [
        ('校验通过', '直接输出，延迟 < 5ms'),
        ('校验未通过', '触发重生成（最多 3 次），每次重生成均重新校验'),
        ('3 次仍未通过', '降级为"安全回复模板"——系统从预设的人格安全语料库中选取最匹配当前语境的保守回复，确保输出内容不偏离人格设定'),
    ])

    add_para(doc, '校验算法基于轻量级 BERT 分类器实现，单次推理延迟 < 80ms，不显著影响对话流畅度。安全回复模板库按人格类型预分类，覆盖"安慰 / 鼓励 / 倾听 / 沉默"四种基础情感响应模式，确保降级输出仍有情感温度。')

    # ---- 第三层 ----
    add_heading(doc, '第三层：长期记忆对齐层（跨会话约束）', level=3)
    add_para(doc, '跨会话场景下，AI 可能因上下文窗口截断而"遗忘"此前对话中建立的个性化表达习惯。该层通过长期记忆摘要机制解决：每轮对话结束时，系统自动提取本轮对话中的"人格特征增量"（如用户新纠正的表达方式、新确认的偏好），以结构化摘要形式追加至人格锚定档案的"动态记忆"区段。后续对话的 system prompt 包含完整的静态锚定 + 动态记忆，确保数字人格在 100 轮对话后仍能保持与第 1 轮一致的语言风格与情感基调，实现"越聊越像"而非"越聊越散"。')

    add_para(doc, '', indent_first=False, space_before=4)
    add_table(doc,
        headers=['对话轮次', '静态锚定', '动态记忆条目', '人格一致性评分（余弦相似度）'],
        rows=[
            ['第 1 轮', '5 维度', '0', '1.00（基准）'],
            ['第 10 轮', '5 维度', '≈ 12 条', '0.94'],
            ['第 50 轮', '5 维度', '≈ 58 条', '0.89'],
            ['第 100 轮', '5 维度', '≈ 105 条', '≥ 0.85（目标）'],
        ],
        col_widths=[2.5, 2.5, 3.5, 5.5]
    )
    add_para(doc, '', indent_first=False, space_before=2)
    add_para(doc, '表 4-7  长期记忆对齐层人格一致性衰减预测', size=9, color=COLOR['muted'], align=WD_ALIGN_PARAGRAPH.CENTER, indent_first=False)

    # ---- 第四层 ----
    add_heading(doc, '第四层：用户纠偏与情感安全兜底层（输出端兜底）', level=3)
    add_para(doc, '即便前三层机制全部生效，仍可能存在用户主观感知的 OOC 体验。该层提供两项兜底能力：')

    add_bullets(doc, [
        ('一键纠偏', '用户在任何对话轮次中点击"这不像 TA"按钮，系统立即将该轮 AI 回复标记为 OOC 负样本，同时弹出轻量纠偏表单（"TA 更可能说……"文本框），用户可自由填写修正内容或跳过。标记数据同时反馈至第二层校验分类器的训练集，实现持续优化。'),
        ('情感安全熔断', '当单次会话内触发 ≥ 3 次"这不像 TA"标记时，系统判定当前人格模型存在系统性偏移风险，自动触发会话暂停并推送"今日对话已保存，TA 需要休息一下"的安全提示，同时将该人格档案标记为"待校准"状态，需用户重新确认锚定档案后方可恢复对话。熔断机制的触发阈值可由用户在设置中自行调整（1–5 次），默认值为 3 次，尊重不同用户对一致性的容忍度差异。'),
    ])

    # 四层闭环总结
    add_para(doc, '', indent_first=False, space_before=6)
    add_callout(doc, '四层闭环', '预防（锚定） → 校验（实时） → 对齐（跨会话） → 兜底（用户触发），将 OOC 发生率控制在可量化、可追溯、可纠偏的范围内。MVP 阶段目标：单次会话 OOC 率 < 5%，跨 50 轮对话人格一致性评分 > 0.85，用户纠偏反馈闭环响应时间 < 24 小时。', 'accent')

    page_break(doc)

    # ==========================================================
    # 联动更新索引
    # ==========================================================
    add_heading(doc, '附录：主文档联动更新索引', level=1)

    add_para(doc, '以下为主文档需配套更新的位置与内容，供主文档修订时参照：')

    add_table(doc,
        headers=['主文档章节', '联动位置', '更新内容'],
        rows=[
            ['第六章 6.5', 'Token 使用场景对照表', '新增"VR 场景包解锁"消耗 200 仪式 Token / 个；"语音对话"消耗 2 对话 Token / 轮'],
            ['第六章 6.6', '充值套餐', '新增"VR 旅行季卡" ¥299 / 季（含 10 个旅行场景包 + 无限语音额度）'],
            ['第六章 6.8', '反情感剥削机制', '新增"VR 空间单次停留时长上限 45 分钟"与"数字人格不得主动发起 VR 邀请"'],
            ['第六章 6.10', '剧情卡池系统', '新增"中年分区改为每日自动推送 1 张场景卡，无需手动抽取"'],
            ['第七章', '财务预测', 'Y3 营收中拆分 VR 业务线预测（¥320 万，占 Y3 总营收 7.4%）'],
            ['第十二章', '投资亮点', '新增"VR 同行空间锁定中年高净值群体，ARPPU 预计为青年分区 3.2 倍"'],
        ],
        col_widths=[3.0, 3.5, 9.5]
    )
    add_para(doc, '', indent_first=False, space_before=2)
    add_para(doc, '附表 1  主文档联动更新索引', size=9, color=COLOR['muted'], align=WD_ALIGN_PARAGRAPH.CENTER, indent_first=False)

    # ==========================================================
    # 保存
    # ==========================================================
    doc.save(OUTFILE)
    size_kb = os.path.getsize(OUTFILE) / 1024
    print(f'Supplement saved: {OUTFILE}  ({size_kb:.1f} KB)')

if __name__ == '__main__':
    build_supplement()
