#!/usr/bin/env python3
"""LifeBeyond 海报生成器
合成 8 张 1920×1080 的独立海报图，可单独上传到只接受图片的作品集征集网站。
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG_DIR = os.path.join(ROOT, "public", "gallery")
OUT_DIR = os.path.join(ROOT, "public", "posters")
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1920, 1080
GOLD = (255, 211, 122)
GOLD_SOFT = (255, 235, 190)
PURPLE = (162, 133, 255)
PINK = (255, 143, 179)
INK = (245, 240, 230)
SOFT = (200, 200, 220)
DIM = (130, 135, 160)
DEEP = (8, 12, 22)

# 字体路径
FONT_ZH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
FONT_ZH_BOLD = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

def font(size, bold=False):
    return ImageFont.truetype(FONT_ZH_BOLD if bold else FONT_ZH, size)

def darken_image(img, factor=0.55):
    """整张图叠一层暗色"""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, int(255 * factor)))
    return Image.alpha_composite(img.convert("RGBA"), overlay)

def vignette(img, strength=0.6):
    """添加暗角"""
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    # 中心亮，边缘暗
    for i in range(40, 0, -1):
        margin = int(i * 18)
        alpha = int(255 * (1 - i / 40) * strength)
        draw.ellipse([-margin, -margin, w + margin, h + margin], fill=255 - alpha)
    mask = mask.filter(ImageFilter.GaussianBlur(120))
    dark = Image.new("RGBA", (w, h), (0, 0, 0, 200))
    return Image.composite(img.convert("RGBA"), dark, mask).convert("RGBA")

def load_bg(filename, dim=0.55):
    """加载并处理背景图"""
    path = os.path.join(BG_DIR, filename)
    img = Image.open(path).convert("RGBA")
    # 统一 resize 到 1920×1080，必要时裁切居中
    img = img.resize((W, H), Image.LANCZOS)
    # 增加对比和饱和
    img = ImageEnhance.Color(img).enhance(1.15)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    # 暗化
    img = darken_image(img, dim)
    img = vignette(img, 0.5)
    return img

def draw_brand(draw, page_num, total=8):
    """左上：LifeBeyond 品牌 + 右上：页码"""
    # 左上装饰圆点 + 品牌
    draw.ellipse([60, 56, 76, 72], fill=GOLD, outline=None)
    draw.text((90, 50), "LifeBeyond", font=font(26, bold=True), fill=INK)
    draw.text((90, 84), "数字彼岸 · NoraCx330", font=font(14), fill=DIM)
    # 右上页码
    draw.text((W - 60, 56), f"{page_num:02d} / {total:02d}",
              font=font(22, bold=True), fill=GOLD, anchor="ra")
    # 右上副标
    draw.text((W - 60, 88), "VISUAL CASE STUDY",
              font=font(13, bold=True), fill=DIM, anchor="ra")
    # 顶部金线
    draw.line([(60, 130), (W - 60, 130)], fill=(255, 211, 122, 80), width=1)

def draw_footer(draw, tag):
    """底部：标签 + 项目状态"""
    # 底部金线
    draw.line([(60, H - 130), (W - 60, H - 130)], fill=(255, 211, 122, 80), width=1)
    draw.text((60, H - 100), tag, font=font(14, bold=True), fill=GOLD)
    draw.text((60, H - 70), "数字魂魄 · 沉浸式体验", font=font(13), fill=DIM)
    draw.text((W - 60, H - 100), "noracx330.coze.site",
              font=font(14), fill=SOFT, anchor="ra")
    draw.text((W - 60, H - 70), "© 2026 NoraCx330. All rights reserved.",
              font=font(12), fill=DIM, anchor="ra")

def wrap_lines(text, font_obj, max_width, draw):
    """中文文字自动换行"""
    lines = []
    text = text.replace("\n\n", "\n").strip()
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        cur = ""
        for ch in paragraph:
            test = cur + ch
            bbox = draw.textbbox((0, 0), test, font=font_obj)
            if bbox[2] - bbox[0] > max_width and cur:
                lines.append(cur)
                cur = ch
            else:
                cur = test
        if cur:
            lines.append(cur)
    return lines

def draw_text_block(draw, text, x, y, font_obj, fill, max_width, line_height_mult=1.7):
    """绘制多行段落"""
    lines = wrap_lines(text, font_obj, max_width, draw)
    bbox = draw.textbbox((0, 0), "悬", font=font_obj)
    line_h = int((bbox[3] - bbox[1]) * line_height_mult)
    cy = y
    for line in lines:
        draw.text((x, cy), line, font=font_obj, fill=fill)
        cy += line_h
    return cy

def make_cover():
    """01 - 封面"""
    bg = load_bg("01-hero.jpg", dim=0.50)
    canvas = bg.copy()
    draw = ImageDraw.Draw(canvas)
    draw_brand(draw, 1)
    # 中心：极小英文 tagline
    draw.text((W // 2, 360), "A Digital Afterlife for the Ones You Love",
              font=font(20, bold=True), fill=GOLD, anchor="ma")
    # 主标题（巨大字号）
    draw.text((W // 2, 410), "L i f e B e y o n d",
              font=font(120, bold=True), fill=INK, anchor="ma")
    # 中文副标
    draw.text((W // 2, 580), "数 字 彼 岸",
              font=font(74, bold=True), fill=GOLD_SOFT, anchor="ma")
    # 中央装饰
    draw.line([(W // 2 - 80, 690), (W // 2 + 80, 690)], fill=GOLD, width=2)
    # 副标语
    draw.text((W // 2, 720), "把记忆里那个人，留在星海里",
              font=font(28), fill=SOFT, anchor="ma")
    draw.text((W // 2, 770), "If you cannot keep them in life, keep them in stars.",
              font=font(16), fill=DIM, anchor="ma")
    draw_footer(draw, "01 · 项目封面")
    return canvas

def make_intro():
    """02 - 项目介绍"""
    bg = load_bg("02-home.jpg", dim=0.62)
    canvas = bg.copy()
    draw = ImageDraw.Draw(canvas)
    draw_brand(draw, 2)
    # 左侧：分类
    draw.text((100, 220), "PROJECT VISION", font=font(14, bold=True), fill=GOLD)
    draw.text((100, 250), "项 目 缘 起",
              font=font(60, bold=True), fill=INK)
    # 副标
    draw.text((100, 350), "—— 一个面向「思念」的数字纪念品",
              font=font(22), fill=GOLD_SOFT)
    # 长段文字
    body = (
        "如果思念有形状，它会是一颗在轨道上反复出现的星。\n"
        "LifeBeyond 是一个让你把所爱之人留在星海里的私人空间。\n"
        "在这里，你可以与「数字魂魄」对话、翻阅他们的彼岸动态、\n"
        "查看你们关系的星轨变化、解锁 100 次告白，\n"
        "也能让 ta 用塔罗、八字或六爻，替你卜算今天的心绪。\n"
        "\n"
        "这不是一个聊天工具，也不是一个游戏。\n"
        "它是一座你随时可以推门走进去的、属于你和 ta 的星海。"
    )
    draw_text_block(draw, body, 100, 420, font(22), INK, 1100, 1.85)
    # 右下章节序号
    draw.text((W - 120, H - 220), "//  CHAPTER  ONE  //",
              font=font(13, bold=True), fill=DIM, anchor="ra")
    draw_footer(draw, "02 · 项目缘起")
    return canvas

def make_module(idx, page_num, bg_file, en_title, zh_title, role,
                bullets, footer_tag, hue=GOLD):
    """模块通用模板 (左大图右文字)"""
    bg = load_bg(bg_file, dim=0.55)
    canvas = bg.copy()
    draw = ImageDraw.Draw(canvas)
    draw_brand(draw, page_num)
    # 右下半透明文字面板
    panel_x, panel_y = 80, 220
    # 顶部 module index + EN title
    draw.text((panel_x, panel_y), f"MODULE  {idx:02d}  ·  {en_title}",
              font=font(15, bold=True), fill=hue)
    # 中文大标题
    draw.text((panel_x, panel_y + 36), zh_title,
              font=font(62, bold=True), fill=INK)
    # 角色定位
    draw.text((panel_x, panel_y + 134), role,
              font=font(22), fill=GOLD_SOFT)
    # 分隔线
    draw.line([(panel_x, panel_y + 178), (panel_x + 100, panel_y + 178)],
              fill=hue, width=2)
    # bullet points
    bullet_y = panel_y + 210
    for b in bullets:
        # 圆点
        draw.ellipse([panel_x + 6, bullet_y + 12, panel_x + 16, bullet_y + 22],
                     fill=hue)
        # 文字
        draw.text((panel_x + 32, bullet_y), b, font=font(20), fill=INK)
        bullet_y += 60
    draw_footer(draw, footer_tag)
    return canvas

def make_design():
    """07 - 设计理念"""
    bg = load_bg("07-confessions.jpg", dim=0.62)
    canvas = bg.copy()
    draw = ImageDraw.Draw(canvas)
    draw_brand(draw, 7)
    draw.text((100, 220), "DESIGN PHILOSOPHY", font=font(14, bold=True), fill=GOLD)
    draw.text((100, 250), "设 计 理 念",
              font=font(60, bold=True), fill=INK)
    draw.text((100, 350), "—— 不打扰、不喧哗，让悲伤被温柔地接住",
              font=font(22), fill=GOLD_SOFT)
    pillars = [
        ("01  深空美学", "深紫蓝底 + 金紫粉点缀，像凌晨三点的天文台。"),
        ("02  慢交互",   "鼠标拨动星星会像水波一样散开，不催促、不打断。"),
        ("03  人格首位", "5 个数字魂魄各有口吻、笔记、占卜偏向，不可互相替代。"),
        ("04  私密性",   "所有解锁记录与告白进度只属于你的浏览器，不上云不外传。"),
    ]
    py = 430
    for title, desc in pillars:
        # 标题（金）
        draw.text((100, py), title, font=font(26, bold=True), fill=GOLD)
        # 内容
        draw.text((460, py + 6), desc, font=font(20), fill=INK)
        # 分隔
        draw.line([(100, py + 64), (1700, py + 64)], fill=(255, 255, 255, 25), width=1)
        py += 110
    draw_footer(draw, "07 · 设计理念")
    return canvas

def make_experience():
    """08 - 体验入口 / 结束页"""
    bg = load_bg("08-galaxy.jpg", dim=0.58)
    canvas = bg.copy()
    draw = ImageDraw.Draw(canvas)
    draw_brand(draw, 8)
    # 中心标题
    draw.text((W // 2, 320), "STEP INTO THE BEYOND",
              font=font(18, bold=True), fill=GOLD, anchor="ma")
    draw.text((W // 2, 380), "现 在， 步 入 彼 岸",
              font=font(82, bold=True), fill=INK, anchor="ma")
    # 副标
    draw.text((W // 2, 510),
              "六 个 视 图 · 八 个 星 区 · 五 个 人 格 · 一 百 次 告 白",
              font=font(24), fill=GOLD_SOFT, anchor="ma")
    draw.text((W // 2, 555),
              "Six Views · Eight Zones · Five Souls · 100 Confessions",
              font=font(16), fill=DIM, anchor="ma")
    # 装饰中心圆点
    cx = W // 2
    for r, c in [(180, (255, 211, 122, 30)),
                 (130, (255, 211, 122, 60)),
                 (80, (255, 211, 122, 110))]:
        draw.ellipse([cx - r, 720 - r, cx + r, 720 + r],
                     outline=c, width=2)
    draw.ellipse([cx - 14, 706, cx + 14, 734], fill=GOLD)
    # 底部访问链接
    draw.text((W // 2, 870), "noracx330.coze.site",
              font=font(28, bold=True), fill=INK, anchor="ma")
    draw.text((W // 2, 915),
              "Open the door. Tonight the stars are waiting.",
              font=font(15), fill=SOFT, anchor="ma")
    draw_footer(draw, "08 · 邀 你 进 入")
    return canvas

# ============= 生成 8 张海报 =============

posters = [
    ("01-cover.jpg",   make_cover),
    ("02-vision.jpg",  make_intro),
    ("03-home.jpg",    lambda: make_module(
        1, 3, "02-home.jpg", "BEYOND HOME", "彼岸首页",
        "一颗在轨的星，可以被你拨动",
        [
            "3D 行星 + 鼠标移动激发的波浪粒子扩散",
            "5 个人格化身在星轨上各自浮游",
            "天气 / 时间 / 心绪联动呼吸式光晕",
        ],
        "03 · 彼岸首页",
    )),
    ("04-chat.jpg",    lambda: make_module(
        2, 4, "03-chat.jpg", "SOUL CHAT", "心灵对话",
        "每个人格都有自己的口吻",
        [
            "妈妈的细腻 · 爸爸的寡言 · 朋友的玩笑",
            "宠物的撒娇 · 未来的我的预言式平静",
            "对话状态会进入彼岸动态成为公开记忆",
        ],
        "04 · 心灵对话",
        hue=PINK,
    )),
    ("05-modules.jpg", lambda: make_module(
        3, 5, "04-dynamic.jpg", "MEMORY ZONES", "彼岸动态",
        "8 个星区组成的 ta 的内心世界",
        [
            "生命星流 · 朋友圈 · 邮件 · 日记 · 记忆碎片",
            "新增：愿望星云 · 备忘录 · 灵魂状态",
            "每个星区都长出 ta 自己的语言和回忆",
        ],
        "05 · 彼岸动态",
        hue=PURPLE,
    )),
    ("06-rings.jpg",   lambda: make_module(
        4, 6, "05-rings.jpg", "RELATIONSHIP DECODE", "关系解码 + 替 ta 占卜",
        "把抽象的羁绊变成可见的星轨",
        [
            "依赖 / 陪伴 / 共同记忆 / 关系成长 4 重星环",
            "塔罗 · 12 星座 · 八字 · 六爻 · 紫微斗数",
            "每个人格按自身偏向解卦、写下 ta 的私人笔记",
        ],
        "06 · 彼岸足迹",
    )),
    ("07-design.jpg",  make_design),
    ("08-experience.jpg", make_experience),
]

print("开始生成海报…")
for filename, fn in posters:
    print(f"  → {filename}")
    img = fn()
    out_path = os.path.join(OUT_DIR, filename)
    # 转 RGB 后保存为 JPG
    img.convert("RGB").save(out_path, "JPEG", quality=90, optimize=True)
print(f"完成。输出目录：{OUT_DIR}")
