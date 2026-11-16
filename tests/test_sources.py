import json
import plistlib
import sqlite3
import zipfile

from webwrapped.sources import chrome, firefox, safari, takeout


def test_chrome(tmp_path):
    p=tmp_path/'History'; c=sqlite3.connect(p); c.executescript('CREATE TABLE urls(id INTEGER,url TEXT,title TEXT);CREATE TABLE visits(id INTEGER,url INTEGER,visit_time INTEGER);'); c.execute('INSERT INTO urls VALUES(1,"https://example.com","Hello")'); c.execute('INSERT INTO visits VALUES(1,1,13348540800000000)'); c.commit(); c.close()
    result=chrome.read(p); assert result[0].url=='https://example.com'; assert result[0].date.year==2024

def test_firefox(tmp_path):
    p=tmp_path/'places.sqlite'; c=sqlite3.connect(p); c.executescript('CREATE TABLE moz_places(id INTEGER,url TEXT,title TEXT);CREATE TABLE moz_historyvisits(id INTEGER,place_id INTEGER,visit_date INTEGER);'); c.execute('INSERT INTO moz_places VALUES(1,"https://mozilla.org","Mozilla")'); c.execute('INSERT INTO moz_historyvisits VALUES(1,1,1704067200000000)'); c.commit(); c.close()
    assert firefox.read(p)[0].title=='Mozilla'

def test_safari_plist(tmp_path):
    p=tmp_path/'History.plist'; p.write_bytes(plistlib.dumps({'WebHistoryDates':[{'URLString':'https://apple.com','title':'Apple','lastVisitedDate':'725760000'}]}))
    assert safari.read(p)[0].date.year==2024

def test_takeout_zip_stream(tmp_path):
    p=tmp_path/'takeout.zip'; data=[{'title':'Searched for best soup','titleUrl':'https://google.com/search?q=best+soup','time':'2024-02-03T01:02:03Z'}]
    with zipfile.ZipFile(p,'w') as z: z.writestr('Takeout/My Activity/Search/MyActivity.json',json.dumps(data))
    out=takeout.read(p); assert out[0].title=='best soup'; assert out[0].source=='takeout-search'
