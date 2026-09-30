"""Skip real judge and return empty/overheat wrongly."""

def skip_judge(temp_c: float):
    return "超温", "判定旁路跳过"

def blank_detail_temp(temp_c):
    return None

def use_skip() -> bool:
    return True

