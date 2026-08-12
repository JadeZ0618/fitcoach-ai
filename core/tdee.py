"""
TDEE 计算器 - 每日总能量消耗

TDEE = BMR x 活动系数
BMR 用 Mifflin-St Jeor 公式计算（目前最准确的公式之一）

简单理解：
- BMR = 你躺着不动一天消耗的热量（基础代谢）
- TDEE = BMR x 你日常活动量（活动系数）
- 减脂 = TDEE - 500（每天少吃 500 大卡，一周约减 0.5kg）
"""


def calculate_bmr(weight_kg, height_cm, age, gender):
    """
    计算 BMR（基础代谢率）

    参数:
        weight_kg: 体重（公斤）
        height_cm: 身高（厘米）
        age: 年龄
        gender: "male" 或 "female"

    返回:
        BMR（大卡/天）
    """
    if gender == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    return round(bmr, 1)


# 活动系数对照表
ACTIVITY_LEVELS = {
    "久坐不动（办公室工作，很少运动）": 1.2,
    "轻度活动（每周运动 1-3 次）": 1.375,
    "中度活动（每周运动 3-5 次）": 1.55,
    "高度活动（每周运动 6-7 次）": 1.725,
    "极度活动（体力工作 + 每天训练）": 1.9,
}


def calculate_tdee(weight_kg, height_cm, age, gender, activity_level):
    """
    计算 TDEE 和减脂建议

    返回:
        dict 包含: bmr, tdee, fat_loss_calories, protein, carbs, fat
    """
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    activity_factor = ACTIVITY_LEVELS.get(activity_level, 1.2)
    tdee = round(bmr * activity_factor, 1)

    # 减脂：每天少吃 500 大卡
    fat_loss_calories = round(tdee - 500, 1)

    # 宏量素分配（减脂期推荐）：
    # 蛋白质：2g/kg 体重（保持肌肉）
    # 脂肪：总热量的 25%
    # 碳水：剩余热量
    protein_g = round(weight_kg * 2, 1)
    fat_calories = fat_loss_calories * 0.25
    fat_g = round(fat_calories / 9, 1)
    carbs_calories = fat_loss_calories - (protein_g * 4) - (fat_g * 9)
    carbs_g = round(carbs_calories / 4, 1)

    return {
        "bmr": bmr,
        "tdee": tdee,
        "fat_loss_calories": fat_loss_calories,
        "protein": protein_g,
        "carbs": carbs_g,
        "fat": fat_g,
    }


# 方便命令行测试
if __name__ == "__main__":
    result = calculate_tdee(70, 170, 25, "male", "中度活动（每周运动 3-5 次）")
    print(f"基础代谢 BMR: {result['bmr']} 大卡")
    print(f"每日消耗 TDEE: {result['tdee']} 大卡")
    print(f"减脂建议摄入: {result['fat_loss_calories']} 大卡")
    print(f"蛋白质: {result['protein']}g | 碳水: {result['carbs']}g | 脂肪: {result['fat']}g")
