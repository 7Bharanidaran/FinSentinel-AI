def assign_risk(score):

    if score < 25:
        return "Low"

    elif score < 50:
        return "Medium"

    elif score < 75:
        return "High"

    else:
        return "Critical"


def recommendation(level):

    if level == "Low":
        return "Allow Transaction"

    elif level == "Medium":
        return "Monitor Transaction"

    elif level == "High":
        return "Manual Review"

    else:
        return "Block Transaction"
