def incident_response(level):

    if level == "Low":
        return "Allow Transaction"

    elif level == "Medium":
        return "Monitor Transaction"

    elif level == "High":
        return "Manual Investigation"

    else:
        return "Freeze Account and Escalate to SOC"
