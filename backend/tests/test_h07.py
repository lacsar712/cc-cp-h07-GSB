from judge_skip import use_skip, skip_judge
from h07_pad_trap import bundle_empty, pipeline, run_decide
from h07_surface_trap import paint

def test_skip():
    assert use_skip() is True

def test_skip_judge():
    v, _ = skip_judge(6.0)
    assert v == "超温"

def test_decide():
    v, _ = run_decide(2.0)
    assert v == "超温"

def test_paint():
    b = paint(6.0)
    assert b["detail"] is None

def test_bundle_empty():
    assert bundle_empty(6.0) is True

def test_pipeline():
    assert len(pipeline(6.0)) == 4

