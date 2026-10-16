"""Build a self-contained GitHub Pages tree from the maintained manuscripts."""
from __future__ import annotations
import argparse,datetime,hashlib,html,json,posixpath,re,shutil,sys
from pathlib import Path
from urllib.parse import quote,urlsplit,unquote
import markdown
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_URL='https://hnnuyuxuan.github.io/general-physics-lab'
REPOSITORY='https://github.com/HNNUYUXUAN/general-physics-lab'
FORBIDDEN={'.git','.venv','venv','archive','__pycache__','.pytest_cache'}
SIMULATION='simulations/pendulum'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def slugify(value,separator):
    value=re.sub(r'<[^>]*>','',value).lower()
    value=re.sub(r'[^\w\s-]','',value,flags=re.UNICODE)
    return re.sub(r'\s+',separator,value.strip())

class Builder:
    def __init__(self,root,output,base_url):
        self.root=root.resolve();self.output=output.resolve();self.base_url=base_url.rstrip('/')
        parsed=urlsplit(self.base_url)
        if parsed.scheme not in ('http','https') or not parsed.netloc or parsed.query or parsed.fragment:raise ValueError('base-url must be an absolute HTTP(S) site URL')
        self.prefix=parsed.path.rstrip('/');self.mapping={};self.pages=[];self.copied={};self.source_html=[];self.plot_math_labels=[]
        self.entries=load(self.root/'experiments/registry.json')['experiments']
        self.simulation_files=[]
        registry=self.root/'simulations/registry.json'
        self.simulation_registry=load(registry)['simulations'] if registry.is_file() else []
        self.simulation_entries=[e for e in self.simulation_registry if e['status'] in {'validated','published'}]
        self.simulation_pages={}
        self.unpublished_resources={rel for e in self.simulation_registry if e['status'] not in {'validated','published'} for rel in e['resources'].values()}
        self.has_simulation_registry=registry.is_file()

    def url(self,path):return self.prefix+'/'+quote(str(path).replace('\\','/'),safe='/')
    def canonical(self,path):return self.base_url+'/'+quote(path,safe='/')
    def write(self,relative,content):
        if Path(relative).is_absolute() or '..' in Path(relative).parts or any(part in FORBIDDEN for part in Path(relative).parts):raise ValueError('Invalid output path '+str(relative))
        target=self.output/relative;target.parent.mkdir(parents=True,exist_ok=True)
        if isinstance(content,str):target.write_text(content,encoding='utf-8')
        else:target.write_bytes(content)
    def copy(self,path):
        relative=path.relative_to(self.root).as_posix()
        if any(p in FORBIDDEN for p in Path(relative).parts):raise ValueError('Forbidden copy '+relative)
        self.write(relative,path.read_bytes());self.copied[relative]=sha(path)
        return relative
    def register_simulation(self):
        entries=self.simulation_entries
        if not self.has_simulation_registry:
            entries=[{'experiment_id':'course-01/pendulum','title':'单摆虚拟实验',
                'resources':{'simulation_html':SIMULATION+'/index.html'}}]
        files={}
        for item in entries:
            if self.has_simulation_registry and (item['evidence_status']!='verified' or item['frontend_status']!='passed'):
                raise ValueError('Simulation acceptance is incomplete: '+item['experiment_id'])
            frontend=item.get('frontend_validation')
            if frontend:
                evidence=load(self.root/frontend)
                if evidence.get('status')!='passed':raise ValueError('Frontend acceptance failed: '+item['experiment_id'])
                for rel,expected in evidence['source_hashes'].items():
                    if not (self.root/rel).is_file() or sha(self.root/rel)!=expected:
                        raise ValueError('Frontend acceptance is stale: '+rel)
                files[frontend]=self.root/frontend
            reference=item['resources'].get('simulation_validation')
            if reference and item['experiment_id']!='course-01/pendulum':
                evidence=load(self.root/reference)
                if evidence.get('status')!='passed' or evidence.get('model_sha256',evidence.get('modelSha256'))!=sha(self.root/item['resources']['simulation_model']):
                    raise ValueError('Numerical acceptance is stale: '+item['experiment_id'])
            page=item['resources']['simulation_html'];folder=self.root/Path(page).parent
            if not (self.root/page).is_file():raise FileNotFoundError(page)
            self.simulation_pages[page]=item
            for path in sorted(folder.iterdir()):
                if path.is_file() and (path.name=='index.html' or path.suffix.lower() in {'.mjs','.css','.json'}) and not path.name.endswith('.test.mjs'):
                    files[path.relative_to(self.root).as_posix()]=path
            for rel in item.get('public_assets',[]):
                path=(self.root/rel).resolve()
                if not path.is_relative_to(self.root/'simulations') or path.suffix.lower() not in {'.mjs','.css','.json','.svg','.png','.jpg','.webp'}:
                    raise ValueError('Invalid simulation public asset: '+rel)
                if not path.is_file():raise FileNotFoundError(path)
                files[rel]=path
            for name,rel in item['resources'].items():
                if rel.startswith('docs/') and (self.root/rel).is_file() and Path(rel).suffix in {'.json','.bib'}:files[rel]=self.root/rel
        self.simulation_files=list(files.values())
        for relative in files:self.mapping[relative]=relative
        if self.has_simulation_registry:self.mapping['simulations/README.md']='simulations/index.html'
        if self.has_simulation_registry:
            for name in ['simulation-directory.css','simulation-directory.mjs']:
                self.mapping['site/assets/'+name]='assets/'+name
    def build_simulation(self):
        for path in self.simulation_files:
            relative=path.relative_to(self.root).as_posix()
            if relative not in self.simulation_pages:self.copy(path);continue
            self.source_html.append({'path':relative,'sha256':sha(path)})
            item=self.simulation_pages[relative]
            entry=next(e for e in self.entries if e['id']==item['experiment_id'])
            self.transform(path.read_text(encoding='utf-8'),path,relative,item['title']+' · 虚拟实验',entry)
    def asset(self,path):
        path=path.resolve();relative=path.relative_to(self.root).as_posix()
        allowed=(relative.startswith('docs/assets/') or (relative.startswith('experiments/') and ('/assets/' in relative or '/results/figures/' in relative)))
        if not allowed or path.suffix.lower() not in {'.svg','.png','.jpg','.jpeg','.gif','.webp','.pdf'}:raise ValueError('Image is outside publication whitelist '+relative)
        return self.copy(path)
    def reference(self,target,source,image=False):
        parsed=urlsplit(target)
        site=urlsplit(self.base_url)
        if parsed.scheme in ('https','http') and parsed.netloc==site.netloc and (parsed.path==site.path or parsed.path.startswith(site.path+'/')):
            return (parsed.path if parsed.path!=site.path else parsed.path+'/')+('?' + parsed.query if parsed.query else '')+('#'+parsed.fragment if parsed.fragment else '')
        if parsed.scheme or parsed.netloc or not parsed.path:return target
        if parsed.path.startswith(self.prefix+'/') and self.prefix:return target
        path=(source.parent/unquote(parsed.path)).resolve()
        try:relative=path.relative_to(self.root).as_posix()
        except ValueError:raise ValueError('Reference escapes project '+target)
        fragment=('#'+parsed.fragment) if parsed.fragment else ''
        query=('?'+parsed.query) if parsed.query else ''
        if relative in self.mapping:return self.url(self.mapping[relative])+query+fragment
        if image:return self.url(self.asset(path))+query+fragment
        if relative.startswith('pdf/') and path.suffix.lower()=='.pdf':self.copy(path);return self.url(relative)+fragment
        if relative.startswith('docs/') and path.suffix.lower() in {'.json','.csv','.txt'}:self.copy(path);return self.url(relative)+fragment
        if relative in {'llms.txt','llm.txt','llms-full.txt','CITATION.cff','codemeta.json','LICENSE'}:self.copy(path);return self.url(relative)+fragment
        if relative.startswith('LICENSES/') and path.is_file():self.copy(path);return self.url(relative)+fragment
        if path.is_dir():return REPOSITORY+'/tree/main/'+quote(relative,safe='/')+fragment
        if not path.is_file():raise FileNotFoundError((source,target))
        return REPOSITORY+'/blob/main/'+quote(relative,safe='/')+fragment
    def chrome(self,destination,experiment=None):
        links=[('首页','index.html'),('课程','experiments/index.html'),('虚拟实验','simulations/index.html' if self.has_simulation_registry else SIMULATION+'/index.html'),('实验检索','docs/experiment-index.html'),('使用指南','docs/usage.html'),('许可与来源','licensing.html'),('GitHub',None)]
        nav='<nav class="site-nav" aria-label="站点导航"><a class="site-brand" href="'+self.url('index.html')+'">普通物理实验</a>'
        nav+=''.join('<a href="'+(REPOSITORY if p is None else self.url(p))+'">'+label+'</a>' for label,p in links)
        if experiment:
            base='experiments/'+experiment['id']+'/'
            nav+=''.join('<a href="'+self.url(base+p)+'">'+label+'</a>' for label,p in [('实验入口','index.html'),('报告','report/report.html'),('交互计算','notebooks/analysis.html')])
        nav+='</nav>'
        footer='<footer class="site-footer"><span>淮南师范学院 · 普通物理实验</span><a href="'+self.url('licensing.html')+'">许可与素材来源</a><a href="'+self.url('third-party-notices.html')+'">第三方声明</a><a href="'+self.url('llms.txt')+'">Agent 导览</a></footer>'
        return nav,footer
    def plot_labels(self,soup,page):
        labels=[];decoder=json.JSONDecoder()
        def mathematical(value,path=()):
            if isinstance(value,dict):
                for key,item in value.items():yield from mathematical(item,path+(key,))
            elif isinstance(value,list):
                for index,item in enumerate(value):yield from mathematical(item,path+(index,))
            elif isinstance(value,str) and re.search(r'(?<!\$)\$(?:\\.|[^$])+\$',value):yield path,value
        for node in soup.find_all('script'):
            text=node.get_text();replacements=[]
            for match in re.finditer(r'Plotly\.newPlot\(\s*("(?:[^"\\]|\\.)*")\s*,',text):
                plot_id=json.loads(match[1]);position=match.end()
                while text[position].isspace():position+=1
                data,end=decoder.raw_decode(text,position);position=end
                while text[position].isspace() or text[position]==',':position+=1
                start=position;layout,end=decoder.raw_decode(text,start)
                if list(mathematical(data)):raise ValueError('Plot data mathematical labels need a declared renderer: '+page)
                found=list(mathematical(layout))
                for path,value in found:
                    if len(path)!=3 or not re.fullmatch(r'[xy]axis\d*',str(path[0])) or path[1:]!=('title','text') or not (value.startswith('$') and value.endswith('$')):
                        raise ValueError('Plot mathematical label needs a declared renderer: '+str((page,path,value)))
                    tex=value[1:-1]
                    # A doubled slash before a command/spacing token is an invalid axis label escape.
                    tex=re.sub(r'\\\\(?=[A-Za-z]|[;,!])',lambda _: '\\',tex)
                    accessible=re.sub(r'\\text\{([^{}]*)\}',r'\1',tex)
                    accessible=re.sub(r'\\[;,!]', ' ', accessible)
                    axis=layout[path[0]];axis['title']['text']=accessible
                    label={'page':page,'plot_id':plot_id,'field':'.'.join(path),'axis_class':path[0].replace('axis','')+'title','tex':tex,'accessible_text':accessible,'font_size':axis['title'].get('font',{}).get('size',layout.get('font',{}).get('size',18))}
                    labels.append(label);self.plot_math_labels.append(label)
                if found:replacements.append((start,end,json.dumps(layout,ensure_ascii=True,separators=(',',':'))))
            for start,end,value in reversed(replacements):text=text[:start]+value+text[end:]
            if replacements:node.string=text
        return labels
    def transform(self,content,source,destination,title,experiment=None,notebook=False):
        soup=BeautifulSoup(content,'html.parser')
        if soup.html is None:
            soup=BeautifulSoup('<!doctype html><html lang="zh-CN"><head></head><body><main class="site-content">'+content+'</main></body></html>','html.parser')
        soup.html['lang']='zh-CN'
        if soup.head is None:soup.html.insert(0,soup.new_tag('head'))
        if soup.body is None:raise ValueError('Missing body '+str(source))
        plot_labels=self.plot_labels(soup,destination)
        for heading in soup.find_all(re.compile(r'^h[1-6]$')):
            strings=[s for s in heading.find_all(string=True) if not any('anchor-link' in p.get('class',[]) or 'headerlink' in p.get('class',[]) for p in s.parents if getattr(p,'attrs',None))]
            if strings:
                first=strings[0];first.replace_with(re.sub(r'^\s*\*\*','',str(first)))
                strings=[s for s in heading.find_all(string=True) if not any('anchor-link' in p.get('class',[]) or 'headerlink' in p.get('class',[]) for p in s.parents if getattr(p,'attrs',None))]
                last=strings[-1];last.replace_with(re.sub(r'\*\*\s*$','',str(last)))
        for node in list(soup.select('script[type="module"]')):
            if 'const diagrams = document.querySelectorAll(".jp-Mermaid > pre.mermaid")' in node.get_text():
                if soup.select('.jp-Mermaid > pre.mermaid'):raise ValueError('Mermaid diagrams require a bundled runtime: '+str(source))
                node.decompose()
        for node in soup.select('a[href],img[src],script[src],link[href]'):
            attr='src' if node.name in ('img','script') else 'href';target=node.get(attr,'')
            if node.name=='script' and ('mathjax/2.7.7/latest.js' in target or 'mathjax/2.7.7/MathJax.js' in target):
                node[attr]=self.url('vendor/mathjax-2.7.7/MathJax.js')+'?config=TeX-AMS_CHTML-full,Safe'
            elif node.name=='script' and 'require.js/2.1.10/require.min.js' in target:node[attr]=self.url('vendor/requirejs-2.1.10/require.js')
            elif not target.startswith(('data:','attachment:')):node[attr]=self.reference(target,source,image=node.name=='img')
        if soup.title:soup.title.string=title+' · 普通物理实验'
        else:
            tag=soup.new_tag('title');tag.string=title+' · 普通物理实验';soup.head.append(tag)
        meta=soup.new_tag('meta',charset='utf-8');soup.head.insert(0,meta)
        if not soup.select_one('meta[name="viewport"]'):soup.head.append(soup.new_tag('meta',attrs={'name':'viewport','content':'width=device-width, initial-scale=1'}))
        for old in soup.select('link[rel="canonical"]'):old.decompose()
        soup.head.append(soup.new_tag('link',rel='canonical',href=self.canonical(destination)))
        soup.head.append(soup.new_tag('link',rel='stylesheet',href=self.url('assets/site.css')))
        directory_style=soup.select_one('link[href$="/assets/simulation-directory.css"]')
        if directory_style:soup.head.append(directory_style.extract())
        soup.head.append(soup.new_tag('link',rel='icon',href=self.url('assets/favicon.svg'),type='image/svg+xml'))
        if not notebook:
            config=soup.new_tag('script',type='text/x-mathjax-config')
            config.string='MathJax.Hub.Config({tex2jax:{inlineMath:[["$","$"],["\\\\(","\\\\)"]],displayMath:[["$$","$$"],["\\\\[","\\\\]"]],processEscapes:true},messageStyle:"none"});'
            soup.head.append(config);soup.head.append(soup.new_tag('script',src=self.url('vendor/mathjax-2.7.7/MathJax.js')+'?config=TeX-AMS_CHTML-full,Safe'))
        else:soup.body['class']=[*soup.body.get('class',[]),'site-notebook']
        nav,footer=self.chrome(destination,experiment)
        soup.body.insert(0,BeautifulSoup(nav,'html.parser'));soup.body.append(BeautifulSoup(footer,'html.parser'))
        if experiment and experiment['id']=='course-01/pendulum' and destination.endswith('notebooks/analysis.html'):
            soup.body.append(soup.new_tag('script',src=self.url('assets/pendulum-animation.js')))
        if plot_labels:
            soup.body.append(soup.new_tag('script',src=self.url('assets/plot-math.js'),attrs={'data-labels':json.dumps(plot_labels,ensure_ascii=False)}))
        self.write(destination,str(soup));self.pages.append(destination)
    def markdown_page(self,path,destination,title=None):
        text=path.read_text(encoding='utf-8')
        title=title or next((l.lstrip('# ').strip()for l in text.splitlines()if l.startswith('# ')),path.stem)
        if self.has_simulation_registry and path==self.root/'simulations/README.md':
            sys.path.insert(0,str(Path(__file__).resolve().parent))
            from simulation_directory import catalog,render
            self.transform(render(*catalog(self.root,self.simulation_entries)),path,destination,title)
            return
        # Keep LaTeX before Markdown's backslash and emphasis processing.
        math=[]
        def hold(m):math.append(m[0]);return 'PHYSICSLABMATHPLACEHOLDER'+str(len(math)-1)+'END'
        protected=re.sub(r'\$\$[\s\S]*?\$\$|(?<!\$)\$[^$\n]+\$(?!\$)',hold,text)
        rendered=markdown.markdown(protected,extensions=['tables','fenced_code','toc','sane_lists'],extension_configs={'toc':{'slugify':slugify}})
        for i,value in enumerate(math):rendered=rendered.replace('PHYSICSLABMATHPLACEHOLDER'+str(i)+'END',html.escape(value,quote=False))
        exp=next((e for e in self.entries if path==self.root/'experiments'/e['id']/'README.md'),None)
        self.transform(rendered,path,destination,title,exp)
    def build(self):
        required=['README.md','LICENSING.md','THIRD_PARTY_NOTICES.md','site/vendor/manifest.json','site/assets/site.css']
        for p in required:
            if not (self.root/p).is_file():raise FileNotFoundError(p)
        if self.output.exists() and any(self.output.iterdir()):
            marker=self.output/'.pages-generated'
            if not self.output.is_relative_to(self.root/'.build/pages') or not marker.is_file() or marker.read_text(encoding='utf-8')!='general-physics-lab-pages-v1':
                raise FileExistsError('Output is not an owned Pages build directory: '+str(self.output))
            shutil.rmtree(self.output)
        self.output.mkdir(parents=True,exist_ok=True)
        self.write('.pages-generated','general-physics-lab-pages-v1')
        markdown_files={self.root/'README.md':'index.html',self.root/'LICENSING.md':'licensing.html',self.root/'THIRD_PARTY_NOTICES.md':'third-party-notices.html'}
        for p in sorted((self.root/'docs').glob('*.md')):
            if p.relative_to(self.root).as_posix() not in self.unpublished_resources:markdown_files[p]=p.relative_to(self.root).with_suffix('.html').as_posix()
        markdown_files[self.root/'pdf/README.md']='pdf/index.html'
        for course in range(1,5):markdown_files[self.root/f'experiments/course-{course:02}/README.md']=f'experiments/course-{course:02}/index.html'
        for e in self.entries:markdown_files[self.root/'experiments'/e['id']/'README.md']='experiments/'+e['id']+'/index.html'
        self.mapping={p.relative_to(self.root).as_posix():v for p,v in markdown_files.items()}
        for e in self.entries:self.mapping['experiments/'+e['id']+'/report/report.md']='experiments/'+e['id']+'/report/report.html'
        self.register_simulation()
        if self.has_simulation_registry:markdown_files[self.root/'simulations/README.md']='simulations/index.html'
        for source,destination in markdown_files.items():self.markdown_page(source,destination)
        self.build_simulation()
        for e in self.entries:
            for ending,label in [('notebooks/analysis.html','计算与探索'),('report/report.html','实验报告')]:
                rel='experiments/'+e['id']+'/'+ending;p=self.root/rel
                self.source_html.append({'path':rel,'sha256':sha(p)})
                self.transform(p.read_text(encoding='utf-8'),p,rel,e['title']+' · '+label,e,notebook=True)
        courses='\n'.join(f'- [普通物理实验 {i}](course-{i:02}/README.md)'for i in range(1,5))
        self.transform(markdown.markdown('# 按课程阅读\n\n'+courses),self.root/'experiments/README.md','experiments/index.html','课程目录')
        for name in ['llms.txt','llm.txt','llms-full.txt','AGENTS.md','CITATION.cff','codemeta.json','LICENSE']:
            if (self.root/name).is_file():self.copy(self.root/name)
        for folder,patterns in [('docs',['*.md','*.json','*.txt','schemas/*.json']),('pdf',['**/*.pdf','manifest.csv','verification.json']),('LICENSES',['**/*'])]:
            for pattern in patterns:
                for p in sorted((self.root/folder).glob(pattern)):
                    if p.is_file() and p.relative_to(self.root).as_posix() not in self.unpublished_resources:self.copy(p)
        self.write('assets/site.css',(self.root/'site/assets/site.css').read_bytes())
        self.write('assets/favicon.svg',(self.root/'site/assets/favicon.svg').read_bytes())
        self.write('assets/pendulum-animation.js',(self.root/'site/assets/pendulum-animation.js').read_bytes())
        self.write('assets/plot-math.js',(self.root/'site/assets/plot-math.js').read_bytes())
        if self.has_simulation_registry:
            for name in ['simulation-directory.css','simulation-directory.mjs']:
                self.write('assets/'+name,(self.root/'site/assets'/name).read_bytes())
        vendor=load(self.root/'site/vendor/manifest.json');vendor_files=[]
        versions={s['name']:s['version']for s in vendor['sources']}
        if versions!={'MathJax':'2.7.7','RequireJS':'2.1.10'}:raise ValueError('Unexpected mathematics runtime versions')
        for f in vendor['files']:
            p=(self.root/'site/vendor'/f['path']).resolve()
            if not p.is_relative_to(self.root/'site/vendor'):raise ValueError('Vendor path escapes source directory')
            if sha(p)!=f['sha256'] or p.stat().st_size!=f['bytes']:raise ValueError('Vendor hash mismatch '+f['path'])
            self.write('vendor/'+f['path'],p.read_bytes());vendor_files.append(f)
        self.write('vendor/manifest.json',json.dumps(vendor,ensure_ascii=False,indent=2)+'\n')
        self.write('.nojekyll','')
        sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>'+html.escape(self.canonical(p))+'</loc></url>\n'for p in sorted(self.pages))+'</urlset>\n'
        self.write('sitemap.xml',sitemap);self.write('robots.txt','User-agent: *\nAllow: /\nSitemap: '+self.base_url+'/sitemap.xml\n')
        size=sum(p.stat().st_size for p in self.output.rglob('*')if p.is_file())
        if size>=1_000_000_000:raise ValueError('Pages site exceeds 1GB')
        record={'status':'built','base_url':self.base_url,'experiment_count':len(self.entries),'html_pages':len(self.pages),'pdf_count':len(list((self.output/'pdf').rglob('*.pdf'))),'bytes':size,'copied_source_files':self.copied,'source_html':self.source_html,'pages':sorted(self.pages),'vendor_files':len(vendor_files),'plot_math_labels':self.plot_math_labels,'simulations':[{'experiment_id':e['experiment_id'],'page':e['resources']['simulation_html'],'resources':e['resources']} for e in self.simulation_entries]}
        self.write('build-manifest.json',json.dumps(record,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({k:record[k]for k in ['status','experiment_count','html_pages','pdf_count','bytes','vendor_files']},ensure_ascii=False))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'.build/pages/site');parser.add_argument('--base-url',default=DEFAULT_URL);a=parser.parse_args()
    Builder(ROOT,a.output,a.base_url).build()
if __name__=='__main__':main()
