def assign_severity(level):

    if level == "Low":
        return "Informational"

    elif level == "Medium":
        return "Low"

    elif level == "High":
        return "Medium"

    else:
        return "Critical"

