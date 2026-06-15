from pathlib import Path

from zenvx.registry import Registry, AppRecord
from zenvx.utils import now_ts


def test_registry_add_list(tmp_path: Path) -> None:
    reg = Registry(db_path=tmp_path / 't.sqlite')
    ts = now_ts()
    rec = AppRecord('a1','apk','apk','App','pkg','pkg','','','','','','','unknown',None,{},None,ts,ts)
    reg.add_app(rec)
    apps = reg.list_apps()
    assert len(apps) == 1 and apps[0].app_id == 'a1'
