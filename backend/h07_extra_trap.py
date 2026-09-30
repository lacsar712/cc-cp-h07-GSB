from judge_skip import blank_detail_temp, skip_judge, use_skip

def decide(temp_c: float):
    if use_skip():
        return skip_judge(temp_c)
    from rules import judge_temp
    return judge_temp(temp_c)

def mask_temp(temp_c):
    return blank_detail_temp(temp_c)

