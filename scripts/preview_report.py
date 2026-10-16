"""Generate a disposable HTML view of the actual Markdown report."""
from pathlib import Path
import nbformat
from nbconvert import HTMLExporter
ROOT=Path(__file__).resolve().parents[1]
body=(ROOT/'experiments/course-01/pendulum/report/report.md').read_text(encoding='utf-8')
nb=nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell(body)])
html,_=HTMLExporter().from_notebook_node(nb)
html=html.replace('<head>','<head><base href="../../experiments/course-01/pendulum/report/">',1)
out=ROOT/'.build/preview';out.mkdir(parents=True,exist_ok=True)
(out/'report.html').write_text(html,encoding='utf-8')
