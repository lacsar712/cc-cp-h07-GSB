"""判定旁路（已停用）。

历史上这里会跳过真实判定、恒报超温，并把详情温度抹成空值，导致
8℃ 以内的偶发读数进不了合格单、单卡与排队栏都看不到数值。
现在统一回落到 rules.judge_temp，任何调用方拿到的都是真实结论与数值。
"""


def use_skip() -> bool:
    # 旁路开关永久关闭：判定必须走真实温度规则。
    return False


def skip_judge(temp_c: float):
    # 即便旧调用方误走到这里，也回落到真实判定，不得再局部放行。
    from rules import judge_temp

    return judge_temp(float(temp_c))


def blank_detail_temp(temp_c):
    # 名称保留以兼容旧引用；详情温度必须是真实数值，不得抹空。
    return float(temp_c)
