"""Check the generated Pages tree, links, local runtime and publication boundary."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
from urllib.parse import urlsplit,unquote
from xml.etree import ElementTree
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
FORBIDDEN={'.git','.venv','venv','archive','__pycache__','.pytest_cache'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def check(site):
    site=site.resolve();manifest=json.loads((site/'build-manifest.json').read_text(encoding='utf-8'))
    base=manifest['base_url'];prefix=urlsplit(base).path.rstrip('/');checks=[];errors=[];local_links=0
    registry=json.loads((ROOT/'experiments/registry.json').read_text(encoding='utf-8'))['experiments']
    assert len(registry)==manifest['experiment_count']==45
    pages=manifest['pages'];assert len(pages)==len(set(pages))
    for relative in pages:
        p=site/relative;soup=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
        canonical=soup.select_one('link[rel="canonical"]')
        if not canonical or unquote(canonical['href'])!=base+'/'+relative:errors.append([relative,'canonical'])
        if not soup.select_one('nav.site-nav') or not soup.select_one('footer.site-footer'):errors.append([relative,'navigation/footer'])
        if not soup.title or not soup.title.get_text(strip=True):errors.append([relative,'title'])
        scripts=[n['src']for n in soup.select('script[src]')]
        if not any('/vendor/mathjax-2.7.7/MathJax.js?'in v for v in scripts):errors.append([relative,'local MathJax'])
        for node in soup.select('a[href],img[src],script[src],link[href]'):
            value=node.get('href',node.get('src',''));parsed=urlsplit(value)
            if parsed.scheme or parsed.netloc:
                if node.name=='script' and parsed.scheme in ('http','https'):errors.append([relative,'external runtime',value])
                continue
            if not parsed.path:continue
            raw=unquote(parsed.path)
            if raw.startswith('/'):
                if prefix and not raw.startswith(prefix+'/'):errors.append([relative,'base path escaped',value]);continue
                target=site/raw[len(prefix):].lstrip('/')
            else:target=p.parent/raw
            target=target.resolve()
            if not target.is_relative_to(site):errors.append([relative,'link escapes site',value]);continue
            if target.is_dir():target=target/'index.html'
            if not target.is_file():errors.append([relative,'missing local target',value])
            local_links+=1
    for e in registry:
        for path in ['index.html','notebooks/analysis.html','report/report.html']:
            assert (site/'experiments'/e['id']/path).is_file(),(e['id'],path)
    for source in manifest['source_html']:
        if sha(ROOT/source['path'])!=source['sha256']:errors.append([source['path'],'source changed during build'])
        # Inline Plotly bytes are retained by the HTML parser; their signatures remain accessible.
        original=(ROOT/source['path']).read_text(encoding='utf-8');published=(site/source['path']).read_text(encoding='utf-8')
        if original.count('Plotly.newPlot')!=published.count('Plotly.newPlot'):errors.append([source['path'],'Plotly initialization count'])
    for rel,digest in manifest['copied_source_files'].items():
        if sha(site/rel)!=digest:errors.append([rel,'copied resource hash'])
    vendor=json.loads((site/'vendor/manifest.json').read_text(encoding='utf-8'))
    for f in vendor['files']:
        p=site/'vendor'/f['path']
        if not p.is_file() or p.stat().st_size!=f['bytes'] or sha(p)!=f['sha256']:errors.append([f['path'],'vendor resource hash'])
    for source in vendor['sources']:
        if not (site/'vendor'/source['license_file']).is_file():errors.append([source['name'],'vendor license'])
    for name in ['site.css','favicon.svg','pendulum-animation.js']:
        if sha(site/'assets'/name)!=sha(ROOT/'site/assets'/name):errors.append(['assets/'+name,'site runtime source hash'])
    animated='experiments/course-01/pendulum/notebooks/analysis.html'
    for relative in pages:
        published=(site/relative).read_text(encoding='utf-8')
        if ('/assets/pendulum-animation.js' in published)!=(relative==animated):errors.append([relative,'animation runtime scope'])
    for rel in ['assets/pendulum-animation.js','vendor/mathjax-2.7.7/MathJax.js','vendor/mathjax-2.7.7/config/TeX-AMS_CHTML-full.js','vendor/mathjax-2.7.7/extensions/Safe.js','vendor/mathjax-2.7.7/jax/output/CommonHTML/jax.js','vendor/requirejs-2.1.10/require.js','llms.txt','llms-full.txt','docs/experiments.json','licensing.html','third-party-notices.html','sitemap.xml','robots.txt','.nojekyll']:
        if not (site/rel).is_file():errors.append([rel,'required file'])
    files=[p for p in site.rglob('*')if p.is_file()]
    for p in files:
        rel=p.relative_to(site)
        if any(q in FORBIDDEN for q in rel.parts):errors.append([rel.as_posix(),'forbidden path'])
        if p.suffix.lower()in {'.ipynb','.nb','.paclet'}:errors.append([rel.as_posix(),'large download belongs on GitHub'])
    size=sum(p.stat().st_size for p in files)
    if size>=1_000_000_000:errors.append(['site','exceeds 1GB',size])
    pdfs=list((site/'pdf').rglob('*.pdf'))
    if len(pdfs)!=57:errors.append(['pdf','expected 57',len(pdfs)])
    sitemap=ElementTree.parse(site/'sitemap.xml');locs=sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
    if len(locs)!=len(pages):errors.append(['sitemap','page count'])
    record={'status':'passed'if not errors else 'failed','experiments':len(registry),'html_pages':len(pages),'pdfs':len(pdfs),'local_links':local_links,'vendor_files':len(vendor['files']),'bytes':size,'errors':errors}
    return record

def main():
    p=argparse.ArgumentParser();p.add_argument('--site',type=Path,default=ROOT/'.build/pages/site');p.add_argument('--report',type=Path);a=p.parse_args()
    record=check(a.site);text=json.dumps(record,ensure_ascii=False,indent=2);print(text)
    if a.report:a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(text+'\n',encoding='utf-8')
    if record['status']!='passed':raise SystemExit(1)
if __name__=='__main__':main()
