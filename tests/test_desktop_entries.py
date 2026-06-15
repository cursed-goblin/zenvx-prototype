from zenvx.desktop import DesktopEntry


def test_desktop_render() -> None:
    e = DesktopEntry(name='X', comment='Y', exec_cmd='zenvx launch a', icon='application-x-executable', runtime='apk', app_id='a')
    txt = e.render()
    assert '[Desktop Entry]' in txt and 'X-ZenvX-AppID=a' in txt
