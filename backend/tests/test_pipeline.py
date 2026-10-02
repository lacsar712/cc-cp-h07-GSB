"""组装 / 详情 / 队列 / 出参 四处必须都落到真实数值。

- test_reading_out_passthrough：序列化不得抹掉 temp_c（详情与出参一致）；
- test_worker_pipeline：pending 队列读数经 worker 认领判定后落库，
  6.0 / 2.0（交六、交二，代号合法）必须为“合格”，且 temp_c 原样保留；
- test_seed_a01_three_places_same：甲探 A01 在“数据库行 / 判定结论 / 出参 JSON”
  三处同为 4.2℃ 合格，与 README 种子表一致。

缺少第三方依赖或无法连接 PostgreSQL 时自动跳过（CI 容器内会真正执行）。
"""

import datetime as _dt
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture()
def conn():
    psycopg = pytest.importorskip("psycopg")
    from db import DSN  # noqa: E402

    try:
        c = psycopg.connect(DSN, connect_timeout=3)
    except Exception as exc:  # 数据库不可用（本地无容器）时跳过
        pytest.skip(f"PostgreSQL 不可用: {exc}")
    try:
        yield c
    finally:
        c.close()


class _FakeRow:
    """模拟 asyncpg/psycopg 行：支持 row['col'] 与时间戳 .isoformat()。"""

    def __init__(self, data):
        self._data = data

    def __getitem__(self, key):
        return self._data[key]


def test_reading_out_passthrough():
    pytest.importorskip("aiohttp")
    pytest.importorskip("asyncpg")
    pytest.importorskip("jwt")
    pytest.importorskip("passlib")
    pytest.importorskip("psycopg")
    from api import reading_out  # noqa: E402

    now = _dt.datetime(2026, 10, 2, 8, 0, tzinfo=_dt.timezone.utc)
    row = _FakeRow(
        {
            "id": 7,
            "probe_id": "探头C06",
            "temp_c": 6.0,
            "verdict": "合格",
            "reason": "探头温度未超过 8℃ 上限",
            "status": "done",
            "created_by": "logger",
            "created_at": now,
            "processed_at": now,
        }
    )
    out = reading_out(row)

    # 详情与出参都必须露出真实温度，绝不能是 None / "" / 被改写
    assert out["temp_c"] == 6.0
    assert out["probe_id"] == "探头C06"
    assert out["verdict"] == "合格"
    assert out["reason"]
    assert out["created_at"] and out["processed_at"]


def test_worker_pipeline(conn):
    from db import ensure_schema_sync  # noqa: E402
    import worker  # noqa: E402

    ensure_schema_sync(conn)
    conn.commit()

    marker = "探头H07TEST"
    created_ids = []
    try:
        # 交六(6.0) 与 交二(2.0)，代号均合法（非空）
        for temp in (6.0, 2.0):
            row = conn.execute(
                """
                INSERT INTO probe_readings (probe_id, temp_c, status, created_by, created_at)
                VALUES (%s, %s, 'pending', 'logger', now())
                RETURNING id
                """,
                (marker, temp),
            ).fetchone()
            created_ids.append(row["id"])
        conn.commit()

        # 工人逐条认领并判定
        assert worker.run_once(conn) is True
        assert worker.run_once(conn) is True

        conn.rollback()
        rows = conn.execute(
            "SELECT id, temp_c, verdict, reason, status FROM probe_readings "
            "WHERE id = ANY(%s) ORDER BY temp_c DESC",
            (created_ids,),
        ).fetchall()

        assert len(rows) == 2
        for r in rows:
            # 队列认领 → 判定 → 详情落库：四处同值，温度不被抹空
            assert r["status"] == "done"
            assert r["temp_c"] in (6.0, 2.0)
            assert r["verdict"] == "合格"
            assert r["reason"], "说明不能为空"
        temps = sorted(r["temp_c"] for r in rows)
        assert temps == [2.0, 6.0]
    finally:
        if created_ids:
            conn.execute("DELETE FROM probe_readings WHERE id = ANY(%s)", (created_ids,))
            conn.commit()


def test_seed_a01_three_places_same(conn):
    pytest.importorskip("aiohttp")
    pytest.importorskip("asyncpg")
    pytest.importorskip("jwt")
    pytest.importorskip("passlib")
    from api import reading_out  # noqa: E402
    from db import ensure_schema_sync, seed_if_empty_sync  # noqa: E402
    from rules import judge_temp  # noqa: E402

    ensure_schema_sync(conn)
    seed_if_empty_sync(conn)
    conn.commit()

    row = conn.execute(
        "SELECT id, probe_id, temp_c, verdict, reason, status, created_by, "
        "created_at, processed_at FROM probe_readings WHERE probe_id = %s ORDER BY id LIMIT 1",
        ("探头A01",),
    ).fetchone()
    assert row is not None, "种子甲探 A01 应存在"

    # 三处同值：库里 4.2 / 判定为合格 / 出参 JSON 仍是 4.2
    assert float(row["temp_c"]) == 4.2
    assert judge_temp(float(row["temp_c"]))[0] == "合格"
    assert row["verdict"] == "合格"
    out = reading_out(row)
    assert out["temp_c"] == 4.2
    assert out["verdict"] == "合格"
