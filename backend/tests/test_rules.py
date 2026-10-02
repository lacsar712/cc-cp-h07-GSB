"""纯判定逻辑：不依赖第三方库与数据库。

对应 H07 验收口径：
- 8℃ 以内（含 6.0 / 2.0 / 甲探 4.2 / 边界 8.0）必须判“合格”；
- 超过 8℃（乙探 12.5 等）必须判“超温”。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rules import judge_temp, verdict_for_display  # noqa: E402

PASS_CASES = [2.0, 6.0, 4.2, 8.0, 0.0, -3.5]
FAIL_CASES = [8.01, 12.5, 30.0]


def test_within_limit_is_pass():
    for t in PASS_CASES:
        verdict, reason = judge_temp(t)
        assert verdict == "合格", f"{t}℃ 应判合格，实际 {verdict}"
        assert reason and "8" in reason


def test_over_limit_is_overheat():
    for t in FAIL_CASES:
        verdict, reason = judge_temp(t)
        assert verdict == "超温", f"{t}℃ 应判超温，实际 {verdict}"
        assert reason


def test_boundary_eight_is_pass():
    assert judge_temp(8.0)[0] == "合格"


def test_seed_samples_match_readme():
    # 甲探 A01 = 4.2℃ 合格；乙探 B02 = 12.5℃ 超温（与 README 种子表一致）
    assert judge_temp(4.2)[0] == "合格"
    assert judge_temp(12.5)[0] == "超温"


def test_display_fallback_before_verdict():
    assert verdict_for_display(None, "pending") == "待处理"
    assert verdict_for_display(None, "processing") == "处理中"
    assert verdict_for_display("合格", "done") == "合格"
