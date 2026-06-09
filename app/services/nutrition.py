def calculate_bmr(weight, height, age, gender):
    if gender.lower() == 'male':
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    return (10 * weight) + (6.25 * height) - (5 * age) - 161


def calculate_tdee(bmr, activity_level):
    multipliers = {
        'sedentary': 1.2,
        'lightly_active': 1.375,
        'moderately_active': 1.55,
        'very_active': 1.725,
        'extra_active': 1.9,
    }
    return bmr * multipliers.get(activity_level, 1.2)


def adjust_for_goal(tdee, goal):
    adjustments = {'lose': 0.8, 'maintain': 1.0, 'gain': 1.15}
    return tdee * adjustments.get(goal, 1.0)


def adjust_for_metabolic_type(calories, macros, metabolic_type):
    if metabolic_type == 'fast':
        return {
            'protein': round(calories * 0.25 / 4),
            'carbs': round(calories * 0.55 / 4),
            'fat': round(calories * 0.20 / 9),
        }
    if metabolic_type == 'slow':
        return {
            'protein': round(calories * 0.35 / 4),
            'carbs': round(calories * 0.35 / 4),
            'fat': round(calories * 0.30 / 9),
        }
    return macros


def adjust_for_diet_type(macros, diet_type):
    total = (macros['protein'] * 4) + (macros['carbs'] * 4) + (macros['fat'] * 9)

    ratios = {
        'keto': (0.25, 0.05, 0.70),
        'high_protein': (0.40, 0.30, 0.30),
        'low_fat': (0.30, 0.55, 0.15),
        'vegan': (0.20, 0.60, 0.20),
        'balanced': (0.30, 0.45, 0.25),
    }

    p, c, f = ratios.get(diet_type, ratios['balanced'])
    return {
        'protein': round(total * p / 4),
        'carbs': round(total * c / 4),
        'fat': round(total * f / 9),
    }


def calculate_nutrition(height, weight, age, gender, activity_level, goal, diet_type, metabolic_type):
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    calories = adjust_for_goal(tdee, goal)

    baseline = {
        'protein': round(calories * 0.30 / 4),
        'carbs': round(calories * 0.45 / 4),
        'fat': round(calories * 0.25 / 9),
    }

    diet_adjusted = adjust_for_diet_type(baseline, diet_type)
    final_macros = adjust_for_metabolic_type(calories, diet_adjusted, metabolic_type)

    return {
        'bmr': round(bmr),
        'tdee': round(tdee),
        'daily_calories': round(calories),
        'macros': final_macros,
        'user_info': {
            'height': height,
            'weight': weight,
            'age': age,
            'gender': gender,
            'activity_level': activity_level,
            'goal': goal,
            'diet_type': diet_type,
            'metabolic_type': metabolic_type,
        },
    }
