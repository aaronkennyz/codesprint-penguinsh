# Server keeps this minimal: trust-but-verify (range checks), and store client's derived fields.
# You can later port the same JS engine to Python if you want server-side recompute.

def compute_bp_avg(sbp1, dbp1, sbp2, dbp2):
    if sbp1 is None or dbp1 is None or sbp2 is None or dbp2 is None:
        return None, None
    return round((sbp1 + sbp2) / 2), round((dbp1 + dbp2) / 2)

def compute_bmi(weight, height):
    if not weight or not height or height <= 0:
        return None
    return round(weight / (height * height), 2)
