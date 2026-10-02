from judge_skip import blank_detail_temp, skip_judge, use_skip
from rules import judge_temp


def decide(temp_c: float):
    temp_c = float(temp_c)
    if use_skip():
        # skip_judge 内部已回落到真实判定，这里再兜一层，绝不局部放行。
        return skip_judge(temp_c)
    return judge_temp(temp_c)


def mask_temp(temp_c):
    # 不得抹掉详情数值：始终回传真实温度。
    return blank_detail_temp(temp_c)
