"""
食物营养数据库 - 常见食物的热量和宏量素

数据是每 100g 食物的营养数据
来源：USDA 食物数据库 + 常见中餐食物（简化版）

后续可以接入真实 API 获取更全面的数据
"""

# 食物数据库: {食物名: {热量, 蛋白质, 碳水, 脂肪}}  (每 100g)
FOOD_DATABASE = {
    "鸡胸肉": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
    "鸡蛋（全蛋）": {"calories": 144, "protein": 13, "carbs": 1.1, "fat": 9.5},
    "蛋白": {"calories": 52, "protein": 11, "carbs": 0.7, "fat": 0.2},
    "糙米饭": {"calories": 112, "protein": 2.6, "carbs": 23, "fat": 0.9},
    "白米饭": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
    "红薯": {"calories": 86, "protein": 1.6, "carbs": 20, "fat": 0.1},
    "紫薯": {"calories": 82, "protein": 1.5, "carbs": 18, "fat": 0.2},
    "燕麦": {"calories": 389, "protein": 17, "carbs": 66, "fat": 7},
    "西兰花": {"calories": 34, "protein": 2.8, "carbs": 7, "fat": 0.4},
    "番茄": {"calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2},
    "黄瓜": {"calories": 15, "protein": 0.7, "carbs": 3.6, "fat": 0.1},
    "生菜": {"calories": 15, "protein": 1.4, "carbs": 2.9, "fat": 0.2},
    "牛里脊": {"calories": 250, "protein": 26, "carbs": 0, "fat": 17},
    "牛腱子": {"calories": 160, "protein": 34, "carbs": 0, "fat": 4},
    "三文鱼": {"calories": 208, "protein": 20, "carbs": 0, "fat": 13},
    "虾仁": {"calories": 99, "protein": 24, "carbs": 0.2, "fat": 0.3},
    "龙利鱼": {"calories": 83, "protein": 17, "carbs": 0, "fat": 1.4},
    "豆腐": {"calories": 76, "protein": 8, "carbs": 1.9, "fat": 4.8},
    "香蕉": {"calories": 89, "protein": 1.1, "carbs": 23, "fat": 0.3},
    "苹果": {"calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2},
    "蓝莓": {"calories": 57, "protein": 0.7, "carbs": 14, "fat": 0.3},
    "牛奶（全脂）": {"calories": 61, "protein": 3.2, "carbs": 4.8, "fat": 3.3},
    "牛奶（脱脂）": {"calories": 34, "protein": 3.4, "carbs": 5, "fat": 0.1},
    "希腊酸奶": {"calories": 59, "protein": 10, "carbs": 3.6, "fat": 0.4},
    "全麦面包": {"calories": 247, "protein": 13, "carbs": 41, "fat": 4.2},
    "坚果（混合）": {"calories": 607, "protein": 20, "carbs": 20, "fat": 52},
    "蛋白粉": {"calories": 400, "protein": 80, "carbs": 8, "fat": 6},
}


def search_food(name):
    """
    搜索食物（支持模糊匹配）

    参数:
        name: 食物名称

    返回:
        匹配的食物列表
    """
    results = []
    for food_name, nutrition in FOOD_DATABASE.items():
        if name in food_name or food_name in name:
            results.append({"name": food_name, **nutrition})
    return results


def get_food_nutrition(name, grams=100):
    """
    获取指定重量食物的营养数据

    参数:
        name: 食物名称
        grams: 重量（克），默认 100g

    返回:
        营养数据字典，如果食物不存在返回 None
    """
    if name not in FOOD_DATABASE:
        return None

    base = FOOD_DATABASE[name]
    ratio = grams / 100  # 换算比例

    return {
        "name": name,
        "grams": grams,
        "calories": round(base["calories"] * ratio, 1),
        "protein": round(base["protein"] * ratio, 1),
        "carbs": round(base["carbs"] * ratio, 1),
        "fat": round(base["fat"] * ratio, 1),
    }
