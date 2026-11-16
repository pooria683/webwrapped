import json

from webwrapped.cli import main


def test_demo_json(capsys):
    main(['--demo','--year','2025','--json']); data=json.loads(capsys.readouterr().out)
    assert data['year']==2025 and data['total_visits']>1000

def test_empty_story(tmp_path):
    out=tmp_path/'story.html'; main(['--year','1900','--out',str(out),'--no-open'])
    assert out.exists() and 'Download share card' in out.read_text()
