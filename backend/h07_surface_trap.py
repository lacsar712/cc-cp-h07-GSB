"""Detail / queue empty surfaces when judge is skipped."""

HIDE_DETAIL = True
HIDE_QUEUE = True
HIDE_PARAM = True

def detail_temp(temp_c):
    return None if HIDE_DETAIL else temp_c

def queue_temp(temp_c):
    return "" if HIDE_QUEUE else temp_c

def param_temp(temp_c):
    return None if HIDE_PARAM else temp_c

def paint(temp_c):
    return {
        "detail": detail_temp(temp_c),
        "queue": queue_temp(temp_c),
        "param": param_temp(temp_c),
    }

def looks_empty(bundle: dict) -> bool:
    return bundle.get("detail") in (None, "") and bundle.get("queue") in (None, "")

