from pathlib import Path
import hashlib
import json

def project_root(start=None):
    start = Path(start or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate/'pyproject.toml').is_file() and (candidate/'experiments').is_dir():
            return candidate
    raise FileNotFoundError('Cannot locate project root; start inside the repository.')

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def write_json(path, value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def input_hashes(experiment):
    experiment=Path(experiment)
    return {name:sha256(experiment/name) for name in ('experiment.json','data/measurements.csv','data/diameters.csv','data/provenance.json')}
