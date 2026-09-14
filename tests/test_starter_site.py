"""Release-contract checks for the starter archive and public setup page."""
from pathlib import Path
import hashlib
from html.parser import HTMLParser
import json
import re
import subprocess
import tempfile
import tomllib
import unittest
from urllib.parse import unquote, urlsplit
import zipfile
ROOT=Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.ids=[];self.targets=[];self.links=[];self.pres={};self.active=None;self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if 'data-copy' in a:self.targets.append(a['data-copy'])
        if tag=='a':self.links.append(a.get('href',''))
        if tag=='pre':self.active=a.get('id');self.pres[self.active]=''
    def handle_data(self,data):
        if self.active:self.pres[self.active]+=data
    def handle_endtag(self,tag):
        if tag=='pre':self.active=None

class StarterSite(unittest.TestCase):
    def test_copy_targets_and_local_links_resolve(self):
        for filename in ('index.html','assistant.html'):
            page=Page((ROOT/filename).read_text())
            self.assertEqual(len(page.ids),len(set(page.ids)))
            for target in page.targets:self.assertIn(target,page.pres);self.assertTrue(page.pres[target].strip())
            for link in page.links:
                u=urlsplit(link)
                if u.scheme or u.netloc:continue
                if not u.path:
                    if u.fragment:self.assertIn(u.fragment,page.ids)
                else:
                    dest=ROOT/unquote(u.path)
                    self.assertTrue(dest.is_file(),link)
                    if u.fragment and dest.suffix=='.html':
                        self.assertIn(u.fragment,Page(dest.read_text()).ids,link)
    def test_documented_terminal_commands_download_before_execution(self):
        page=Page((ROOT/'index.html').read_text())
        for key in ['setup-command','setup-command-steps','everything-command','custom-command','model-command']:
            command=page.pres[key].strip()
            self.assertIn('mktemp',command);self.assertIn(' -o "$f" && bash "$f"',command)
            result=subprocess.run(['/bin/bash','-n','-c',command],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
    def test_failed_download_does_not_run_payload_and_returns_failure(self):
        # Exercise the exact site command with a test-owned curl that leaves a
        # complete executable payload but returns failure, as an interrupted transfer can.
        command=Page((ROOT/'index.html').read_text()).pres['setup-command'].strip()
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);(d/'curl').write_text('#!/bin/bash\nwhile [ "$#" -gt 0 ]; do if [ "$1" = -o ]; then printf "echo SHOULD_NOT_RUN\\n" > "$2"; break; fi; shift; done\nexit 22\n');(d/'curl').chmod(0o755)
            import os
            env=dict(os.environ,PATH=str(d)+':/usr/bin:/bin')
            result=subprocess.run(['/bin/bash','-c',command],capture_output=True,text=True,env=env)
            self.assertNotEqual(result.returncode,0);self.assertNotIn('SHOULD_NOT_RUN',result.stdout)
    def test_archive_and_manifest_match_all_starter_files(self):
        source={str(p.relative_to(ROOT/'starter')):p.read_bytes() for p in (ROOT/'starter').rglob('*') if p.is_file()}
        with zipfile.ZipFile(ROOT/'assets/AI-Operations-Starter.zip') as z:
            self.assertEqual(set(z.namelist()),{'AI Operations/'+p for p in source})
            for p,data in source.items():self.assertEqual(z.read('AI Operations/'+p),data,p)
        manifest=json.loads((ROOT/'assets/starter-manifest.json').read_text())
        self.assertEqual(manifest['file_count'],len(source))
        self.assertEqual(manifest['sha256'],{p:hashlib.sha256(data).hexdigest() for p,data in source.items()})
    def test_agent_definitions_have_real_role_files_and_no_global_overrides(self):
        agents=list((ROOT/'starter/.codex/agents').glob('*.toml'));self.assertEqual(len(agents),6)
        for path in agents:
            d=tomllib.loads(path.read_text());self.assertEqual(set(d),{'name','description','developer_instructions'})
            self.assertTrue((ROOT/f'starter/02_Agents/{path.stem}/AGENTS.md').is_file())
            self.assertTrue(all(isinstance(x,str) and x for x in d.values()))
        for path in (ROOT/'starter').rglob('*.json'):json.loads(path.read_text())
    def test_readme_prompt_anchors_exist(self):
        md=(ROOT/'docs/PROMPTS.md').read_text()
        anchors={re.sub(r'[^\w\- ]','',line[3:].strip().lower()).replace(' ','-') for line in md.splitlines() if line.startswith('## ')}
        for anchor in re.findall(r'docs/PROMPTS.md#([^)]*)',(ROOT/'README.md').read_text()):self.assertIn(anchor,anchors)

if __name__=='__main__':unittest.main()
