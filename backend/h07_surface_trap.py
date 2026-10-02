"""判定链路组装出参：详情、排队栏、入参三处都必须露出真实温度数值。"""

# 历史上这三个开关会把 detail/queue/param 抹成 None / 空串，
# 造成单卡看不到数值、排队栏为空。一律关闭遮蔽，落真实数值。
HIDE_DETAIL = False
HIDE_QUEUE = False
HIDE_PARAM = False


def detail_temp(temp_c):
    return None if HIDE_DETAIL else float(temp_c)


def queue_temp(temp_c):
    return "" if HIDE_QUEUE else float(temp_c)


def param_temp(temp_c):
    return None if HIDE_PARAM else float(temp_c)


def paint(temp_c):
    return {
        "detail": detail_temp(temp_c),
        "queue": queue_temp(temp_c),
        "param": param_temp(temp_c),
    }


def looks_empty(bundle: dict) -> bool:
    # 详情与排队栏只要任一露出了真实数值就不算空。
    return bundle.get("detail") in (None, "") and bundle.get("queue") in (None, "")
