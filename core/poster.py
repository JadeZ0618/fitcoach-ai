"""
打卡海报生成模块

功能：
1. 随机生成励志话术供用户选择
2. 用 Pillow 合成打卡海报（用户上传照片做背景 + 日期 + 打分 + 励志话术）

海报布局（16:9）：
┌──────────────────────────────┐
│         2026年8月12日          │  ← 日期（顶部居中）
│                              │
│                              │
│          🎯 92分              │  ← 完成度打分（正中大字）
│        三餐打卡完成！          │  ← 打分下方小字
│                              │
│  "每一口自律，都在雕刻更好的自己"  │  ← 励志话术（底部居中）
│         FitCoach AI           │  ← 品牌名
└──────────────────────────────┘
"""

import random
import io
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# ============================================================
# 励志话术库（减脂 / 励志 / 努力 三个方向）
# ============================================================

MOTIVATIONAL_QUOTES = [
    # 减脂相关
    "每一口自律，都在雕刻更好的自己",
    "今天少吃的每一口，都是明天的马甲线",
    "脂肪不会凭空消失，但汗水不会骗你",
    "你不是在减肥，你是在重新认识自己的身体",
    "管住嘴不是委屈自己，是心疼未来的自己",
    "减脂不是挨饿，是学会和食物做朋友",
    "三个月后的你会感谢现在坚持的你",
    "体重秤上的数字不重要，镜子里的变化才重要",
    # 励志相关
    "坚持别人坚持不了的，才能得到别人得不到的",
    "所有的闪闪发光，都是在暗处默默努力的结果",
    "你现在的自律，是未来自由的入场券",
    "不要等准备好了才开始，开始了才会准备好",
    "每天进步1%，一年后你将强大37倍",
    "世界上最远的距离，是从知道到做到",
    "运气是努力的附属品，没有实力的运气只是偶遇",
    "你不需要很厉害才能开始，但你需要开始才能很厉害",
    # 努力相关
    "汗水是脂肪的眼泪，今天流下的每一滴都算数",
    "自律给我自由，坚持给我答案",
    "不是因为有了希望才坚持，是因为坚持了才有希望",
    "你偷过的每一个懒，都会变成打脸的巴掌",
    "成功的路上并不拥挤，因为坚持的人不多",
    "比起一时的热血，我更相信日复一日的坚持",
    "今天的不舒服，是为了明天的不服输",
    "把坚持变成习惯，把习惯变成性格",
    "每一个不曾起舞的日子，都是对生命的辜负",
    "你流过的汗，终将变成你身上的光",
    "与其羡慕别人，不如自己成为那样的人",
    "人生没有白走的路，每一步都算数",
    "你只管努力，剩下的交给时间",
    "今天的你，要比昨天的你更强一点",
]


def get_random_quotes(n=3):
    """随机返回 n 句励志话术（不重复）"""
    return random.sample(MOTIVATIONAL_QUOTES, min(n, len(MOTIVATIONAL_QUOTES)))


# ============================================================
# 饮食完成度打分
# ============================================================

def calculate_diet_score(logs, user_profile=None):
    """计算当日饮食完成度打分（0-100 分）

    评分规则：
    - 三餐全部记录：基础 70 分
    - 热量在目标范围 ±15% 以内：+15 分
    - 蛋白质达到目标的 60% 以上：+15 分

    Args:
        logs: 今日饮食记录列表（从 get_today_diet_logs 获取）
        user_profile: 用户身体数据 dict（含 weight/height/age/gender/activity_level）

    Returns:
        int: 0-100 的分数
    """
    score = 0

    # 三餐完成情况
    recorded_meals = set()
    total_cal = 0
    total_protein = 0

    for log in logs:
        meal_type = log[9] if len(log) > 9 else "snack"
        recorded_meals.add(meal_type)
        total_cal += log[5] if log[5] else 0
        total_protein += log[6] if log[6] else 0

    breakfast = "breakfast" in recorded_meals
    lunch = "lunch" in recorded_meals
    dinner = "dinner" in recorded_meals
    meal_count = sum([breakfast, lunch, dinner])

    # 基础分：按餐次完成度给分
    if meal_count == 3:
        score += 70
    elif meal_count == 2:
        score += 45
    elif meal_count == 1:
        score += 20

    # 热量达标加分
    if user_profile and total_cal > 0:
        try:
            from core.tdee import calculate_tdee
            result = calculate_tdee(
                user_profile["weight"],
                user_profile["height"],
                user_profile["age"],
                user_profile["gender"],
                user_profile["activity_level"],
            )
            target = result["fat_loss_calories"]
            if target > 0:
                ratio = total_cal / target
                # 在目标 ±15% 以内 +15 分；±25% 以内 +8 分
                if 0.85 <= ratio <= 1.15:
                    score += 15
                elif 0.75 <= ratio <= 1.25:
                    score += 8
        except Exception:
            pass  # 计算失败不影响基础分

        # 蛋白质达标加分
        protein_target = user_profile["weight"] * 1.5  # 简单估算：体重 × 1.5g
        if total_protein >= protein_target * 0.6:
            score += 15
        elif total_protein >= protein_target * 0.4:
            score += 8

    return min(score, 100)


# ============================================================
# 海报生成（Pillow 合成图片）
# ============================================================

# 海报尺寸（16:9）
POSTER_WIDTH = 1080
POSTER_HEIGHT = 608

# 字体路径（Windows 自带中文字体）
_FONT_CANDIDATES = [
    "C:\\Windows\\Fonts\\msyh.ttc",    # 微软雅黑
    "C:\\Windows\\Fonts\\msyhbd.ttc",   # 微软雅黑粗体
    "C:\\Windows\\Fonts\\simhei.ttf",   # 黑体
    "C:\\Windows\\Fonts\\simsun.ttc",   # 宋体
    "/System/Library/Fonts/PingFang.ttc",  # macOS
]


def _load_font(size, bold=False):
    """加载中文字体，按优先级尝试"""
    paths = _FONT_CANDIDATES
    if bold:
        # 优先尝试粗体
        paths = ["C:\\Windows\\Fonts\\msyhbd.ttc"] + paths
    for path in paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    # 兜底：默认字体
    return ImageFont.load_default()


def _crop_to_16_9(img):
    """把图片裁剪/缩放到 16:9 比例"""
    target_ratio = POSTER_WIDTH / POSTER_HEIGHT
    w, h = img.size
    current_ratio = w / h

    if current_ratio > target_ratio:
        # 图片太宽，裁左右
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        # 图片太高，裁上下
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))

    # 缩放到目标尺寸
    img = img.resize((POSTER_WIDTH, POSTER_HEIGHT), Image.LANCZOS)
    return img


def generate_poster(photo_bytes, date_str, score, quote):
    """生成打卡海报

    Args:
        photo_bytes: 用户上传照片的字节数据
        date_str: 日期字符串，如 "2026年8月12日"
        score: 完成度分数 (0-100)
        quote: 用户选择的励志话术

    Returns:
        bytes: PNG 图片的字节数据
    """
    # 1. 打开用户上传的照片，裁剪为 16:9
    photo = Image.open(io.BytesIO(photo_bytes))
    photo = photo.convert("RGB")
    bg = _crop_to_16_9(photo)

    # 2. 创建半透明深色遮罩（让文字更清晰）
    overlay = Image.new("RGBA", (POSTER_WIDTH, POSTER_HEIGHT), (0, 0, 0, 100))
    bg_rgba = bg.convert("RGBA")
    bg_rgba = Image.alpha_composite(bg_rgba, overlay)

    # 转回 RGB 用于绘制
    canvas = bg_rgba.convert("RGB")
    draw = ImageDraw.Draw(canvas)

    # 3. 加载字体
    font_date = _load_font(36)
    font_score = _load_font(96, bold=True)
    font_score_label = _load_font(28)
    font_quote = _load_font(32)
    font_brand = _load_font(22)

    # 4. 绘制日期（顶部居中）
    date_text = date_str
    bbox = draw.textbbox((0, 0), date_text, font=font_date)
    date_w = bbox[2] - bbox[0]
    draw.text(
        ((POSTER_WIDTH - date_w) // 2, 40),
        date_text,
        fill=(255, 255, 255),
        font=font_date,
    )

    # 5. 绘制完成度打分（正中大字）
    # 分数颜色：90+ 金色，70-89 绿色，<70 橙色
    if score >= 90:
        score_color = (255, 215, 0)  # 金色
        medal_text = "★"  # 用五角星代替 emoji（PIL 默认字体不支持 emoji）
    elif score >= 70:
        score_color = (0, 230, 118)  # 绿色
        medal_text = "●"
    else:
        score_color = (255, 167, 38)  # 橙色
        medal_text = "▲"

    score_text = f"{medal_text} {score} 分"
    bbox = draw.textbbox((0, 0), score_text, font=font_score)
    score_w = bbox[2] - bbox[0]
    score_h = bbox[3] - bbox[1]
    score_x = (POSTER_WIDTH - score_w) // 2
    score_y = (POSTER_HEIGHT - score_h) // 2 - 50  # 上移 10px 给下方标签留空间

    # 分数背景圆角矩形（纯黑，提高可读性）
    padding = 24
    box_x1 = score_x - padding
    box_y1 = score_y - padding // 2
    box_x2 = score_x + score_w + padding
    box_y2 = score_y + score_h + padding
    draw.rounded_rectangle(
        [box_x1, box_y1, box_x2, box_y2],
        radius=16,
        fill=(0, 0, 0),
    )

    draw.text((score_x, score_y), score_text, fill=score_color, font=font_score)

    # 6. 打分下方标签（放在分数框外面，紧贴底部）
    label_text = "三餐打卡完成！" if score >= 70 else "继续加油！"
    bbox = draw.textbbox((0, 0), label_text, font=font_score_label)
    label_w = bbox[2] - bbox[0]
    label_y = box_y2 + 16
    draw.text(
        ((POSTER_WIDTH - label_w) // 2, label_y),
        label_text,
        fill=(255, 255, 255),
        font=font_score_label,
    )

    # 7. 绘制励志话术（底部居中）
    # 如果话术太长，自动换行
    quote_lines = _wrap_text(quote, font_quote, POSTER_WIDTH - 120)
    quote_y = POSTER_HEIGHT - 100 - (len(quote_lines) - 1) * 40
    for line in quote_lines:
        bbox = draw.textbbox((0, 0), line, font=font_quote)
        line_w = bbox[2] - bbox[0]
        draw.text(
            ((POSTER_WIDTH - line_w) // 2, quote_y),
            line,
            fill=(255, 255, 255),
            font=font_quote,
        )
        quote_y += 40

    # 8. 品牌名（最底部）
    brand_text = "FitCoach AI"
    bbox = draw.textbbox((0, 0), brand_text, font=font_brand)
    brand_w = bbox[2] - bbox[0]
    draw.text(
        ((POSTER_WIDTH - brand_w) // 2, POSTER_HEIGHT - 35),
        brand_text,
        fill=(180, 180, 180),
        font=font_brand,
    )

    # 9. 导出为 PNG
    output = io.BytesIO()
    canvas.save(output, format="PNG", quality=95)
    return output.getvalue()


def _wrap_text(text, font, max_width):
    """把长文本按像素宽度自动换行（中文字符逐字拆分）"""
    lines = []
    current = ""
    for char in text:
        test = current + char
        bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), test, font=font)
        w = bbox[2] - bbox[0]
        if w > max_width and current:
            lines.append(current)
            current = char
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def get_today_date_str():
    """返回中文日期字符串，如 '2026年8月12日 周三'"""
    now = datetime.now()
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return f"{now.year}年{now.month}月{now.day}日 {weekdays[now.weekday()]}"
