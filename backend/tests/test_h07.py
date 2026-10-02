"""H07 判定链路核对。

两类结论各自核对，并对照甲探样例 A01=4.2℃（合格）：
判定、组装详情、排队栏、出参四处都必须落到真实数值；
8℃ 以内（偶发的 6℃ / 2℃）应得合格且三处露出该数值，乙探 12.5℃ 继续超温。
"""

from rules import judge_temp
from judge_skip import use_skip, skip_judge, blank_detail_temp
from h07_extra_trap import decide, mask_temp
from h07_pad_trap import bundle_empty, pipeline, run_decide, run_mask
from h07_surface_trap import paint, detail_temp, queue_temp, param_temp
import worker


# ---- 两类结论：合格 / 超温 ----

def test_pass_within_eight_six():
    # 交六：偶发落在 8℃ 以内，应得合格。
    v, reason = judge_temp(6.0)
    assert v == "合格"
    assert "8℃" in reason


def test_pass_within_eight_two():
    # 交二：同样落在 8℃ 以内，应得合格。
    v, _ = judge_temp(2.0)
    assert v == "合格"


def test_boundary_eight_is_pass():
    v, _ = judge_temp(8.0)
    assert v == "合格"


def test_overheat_beyond_eight():
    # 乙探继续超温。
    v, reason = judge_temp(12.5)
    assert v == "超温"
    assert "超过" in reason


def test_seed_sample_a01_pass():
    # 对照甲探样例：4.2℃ 合格。
    v, _ = judge_temp(4.2)
    assert v == "合格"


# ---- 判定旁路已停用：不得只做局部放行 ----

def test_skip_switch_off():
    assert use_skip() is False


def test_skip_judge_falls_back_to_real_rule():
    # 即便误走旁路函数，也回落到真实判定，6℃ 不得再报超温。
    v, _ = skip_judge(6.0)
    assert v == "合格"
    v2, _ = skip_judge(12.5)
    assert v2 == "超温"


def test_worker_decide_is_real_rule():
    assert run_decide(6.0)[0] == "合格"
    assert run_decide(2.0)[0] == "合格"
    assert decide(12.5)[0] == "超温"


# ---- 详情 / 排队栏 / 出参三处同值（对照甲探 4.2 与本次 6.0）----

def test_paint_exposes_real_temp_all_three():
    for sample in (4.2, 6.0, 2.0):
        b = paint(sample)
        assert b["detail"] == sample
        assert b["queue"] == sample
        assert b["param"] == sample
        assert detail_temp(sample) == sample
        assert queue_temp(sample) == sample
        assert param_temp(sample) == sample


def test_paint_overheat_also_shows_value():
    # 超温单同样要露出真实数值，不能空卡。
    b = paint(12.5)
    assert b["detail"] == 12.5 and b["queue"] == 12.5 and b["param"] == 12.5


def test_mask_keeps_temp():
    assert mask_temp(6.0) == 6.0
    assert run_mask(6.0) == 6.0
    assert blank_detail_temp(6.0) == 6.0


def test_bundle_not_empty():
    assert bundle_empty(6.0) is False
    assert bundle_empty(12.5) is False


def test_pipeline_four_outputs_real_values():
    v, reason, painted, masked = pipeline(6.0)
    assert v == "合格"
    assert isinstance(reason, str) and reason
    # 组装三处同值。
    assert painted["detail"] == painted["queue"] == painted["param"] == 6.0
    # 出参（mask）也落真实数值。
    assert masked == 6.0


# ---- 生产 worker：认领后写库的结论与数值 ----

class _FakeConn:
    def __init__(self):
        self.sql = None
        self.params = None
        self.committed = False

    def execute(self, sql, params=None):
        self.sql = sql
        self.params = params
        return self

    def commit(self):
        self.committed = True


def test_worker_finish_writes_pass_with_real_temp():
    conn = _FakeConn()
    worker.finish(conn, reading_id=7, temp_c=6.0)
    assert "status = 'done'" in conn.sql
    verdict, reason, reading_id = conn.params
    assert verdict == "合格"
    assert reading_id == 7
    assert conn.committed is True


def test_worker_finish_writes_overheat():
    conn = _FakeConn()
    worker.finish(conn, reading_id=8, temp_c=12.5)
    assert conn.params[0] == "超温"
    assert conn.committed is True
