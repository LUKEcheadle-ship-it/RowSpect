"""Open synthetic RowSpect downloads in Gnumeric and record bounded evidence."""
from __future__ import annotations
import argparse,gzip,hashlib,json,subprocess,time
from pathlib import Path
import xml.etree.ElementTree as ET


def command(*args):
    return subprocess.check_output(args,text=True,stderr=subprocess.STDOUT,timeout=20)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--browser-evidence',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    source=a.browser_evidence.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    receipt=json.loads((source/'receipt.json').read_text())
    assert receipt['decision']=='PASS' and receipt['source_dirty'] is False
    version=command('gnumeric','--version').strip();results=[]
    for name,rows in [('converted.xlsx',4),('cleaned.xlsx',3),('converted.csv',4),('cleaned.csv',3)]:
        path=source/'downloads'/name
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest==receipt['files_sha256'][name]
        native=out/(name+'.gnumeric')
        conversion=subprocess.run(['ssconvert',str(path),str(native)],capture_output=True,text=True,timeout=30)
        (out/(name+'.conversion.log')).write_text(conversion.stdout+conversion.stderr)
        assert conversion.returncode==0 and native.is_file(),conversion.stderr
        payload=native.read_bytes()
        root=ET.fromstring(gzip.decompress(payload) if payload[:2]==b'\x1f\x8b' else payload)
        cells={(int(c.attrib['Row']),int(c.attrib['Col'])):c for c in root.iter() if c.tag.rsplit('}',1)[-1]=='Cell' and 'Row' in c.attrib}
        assert max(row for row,col in cells)==rows
        literal=cells[(1,2)]
        assert literal.attrib.get('ValueType')=='60',ET.tostring(literal)
        assert (literal.text or '').lstrip("'")=='=1+1'
        if name.endswith('.xlsx'):
            assert cells[(1,0)].text=='001' and cells[(1,0)].attrib.get('ValueType')=='60'
        with (out/(name+'.desktop.log')).open('w') as log:
            process=subprocess.Popen(['gnumeric','--no-splash',str(path)],stdout=log,stderr=subprocess.STDOUT)
            try:
                deadline=time.monotonic()+25;window=None;titles=[]
                while time.monotonic()<deadline:
                    if process.poll() is not None: raise RuntimeError(f'{name}: desktop exited before loading')
                    listing=subprocess.run(['xdotool','search','--onlyvisible','--pid',str(process.pid)],capture_output=True,text=True,timeout=5)
                    ids=listing.stdout.split();titles=[]
                    for wid in ids:
                        title=command('xdotool','getwindowname',wid).strip();titles.append(title)
                        if name in title and 'Gnumeric' in title: window=wid
                    if window:
                        if any(any(x in title.lower() for x in ('error','warning','import','recover')) for title in titles):
                            raise RuntimeError(f'{name}: desktop requires intervention: {titles}')
                        break
                    time.sleep(.25)
                assert window is not None,(name,titles)
                command('xdotool','windowsize',window,'1280','850')
                command('xdotool','windowmove',window,'0','0')
                command('xdotool','windowfocus',window)
                time.sleep(1)
                command('import','-window','root',str(out/(name+'.png')))
                assert process.poll() is None
            finally:
                process.terminate()
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
        assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
        results.append({'file':name,'source_sha256':digest,'desktop_window_titles':titles,'native_import_rows':rows,'formula_like_value_is_text':True,'original_unchanged':True})
    result={'decision':'PASS','source_sha':receipt['source_sha'],'browser_receipt_sha256':hashlib.sha256((source/'receipt.json').read_bytes()).hexdigest(),'native_application':version,'results':results,'microsoft_excel_tested':False,'csv_note':'CSV auto-import types are controlled by the spreadsheet application; choose text import for identifiers. Native XLSX string identifiers were checked.'}
    (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
