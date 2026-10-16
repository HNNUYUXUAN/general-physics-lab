"""Synthetic record fixtures; these tests do not represent physics verification."""
import contextlib,hashlib,importlib.util,io,json,tempfile,unittest
from pathlib import Path

BASE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('scientific_index',BASE.parent/'scripts/build_simulation_scientific_index.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)

class PublicIndexTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=BASE);self.root=Path(self.tmp.name)
        self.pdf=b'%PDF-1.4\nsynthetic fixture only\n';self.pdfsha=hashlib.sha256(self.pdf).hexdigest()
        self.entry={'experiment_id':'test/unit-lab','slug':'unit-lab','title':'Fixture','status':'validated',
            'model_version':'1','evidence_status':'verified','frontend_status':'passed',
            'tests':['tests/unit.test.mjs'],'validator':'scripts/validate_unit.py',
            'frontend_validation':'docs/simulation/unit-frontend.json','resources':{
            'simulation_html':'simulations/unit-lab/index.html','simulation_model':'simulations/unit-lab/model.mjs',
            'simulation_controller':'simulations/unit-lab/app.mjs','simulation_styles':'simulations/unit-lab/lab.css',
            'simulation_charts':'simulations/unit-lab/chart.mjs','simulation_observations':'simulations/unit-lab/observations.json',
            'model_evidence':'docs/unit-evidence.md','references_json':'docs/unit-references.json',
            'simulation_validation':'docs/simulation/unit-reference.json'}}
        for path in self.entry['resources'].values():self.write(path,'fixture')
        for path in [*self.entry['tests'],self.entry['validator']]:self.write(path,'fixture')
        self.ref={'id':'fixture','title':'Synthetic fixture','full_text_status':'obtained_and_read',
            'pdf_sha256':self.pdfsha,'locators':[{'page':1,'location':'fixture only'}]}
        self.json('docs/unit-references.json',{'experiment_id':'test/unit-lab','references':[self.ref]})
        self.json('docs/simulation/unit-reference.json',{'status':'passed','modelSha256':self.sha('simulations/unit-lab/model.mjs')})
        resources=self.entry['resources']
        self.front={'status':'passed','source_hashes':{v:self.sha(v)for k,v in resources.items()if k.startswith('simulation_') and k!='simulation_validation'},
            'scientific_evidence':{'status':'verified','decision_source_files':{resources[k]:self.sha(resources[k])for k in ['model_evidence','references_json','simulation_model']},'core_references':[{'id':'fixture','pdf_sha256':self.pdfsha}]}}
        self.json(self.entry['frontend_validation'],self.front)
        self.json('simulations/registry.json',{'experiment_count':1,'simulations':[self.entry]})

    def tearDown(self):self.tmp.cleanup()
    def write(self,path,data):
        p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data,encoding='utf-8');return p
    def json(self,path,data):return self.write(path,json.dumps(data))
    def sha(self,path):return M.digest(self.root/path)
    def run_main(self,*args):
        with contextlib.redirect_stdout(io.StringIO()):return M.main(['--repo-root',str(self.root),*args])

    def test_public_clone_requires_no_local_archive(self):
        data=M.collect(self.root)
        self.assertEqual(data['scientific_ready_count'],1)
        self.assertEqual(data['references'][0]['local_pdf_verification']['status'],'not_requested')
        self.assertNotIn(str(self.root),json.dumps(data))

    def test_check_ignores_runtime_timestamp_and_local_pdf_facts(self):
        self.assertEqual(self.run_main('--require-all-ready'),0)
        p=self.root/'docs/series-scientific-manifest.json';data=M.read(p)
        data['generated_at_utc']='1999-01-01T00:00:00Z';data['local_pdf_verification_requested']=True
        data['references'][0]['local_pdf_verification']={'status':'matched','checked_at':'1999'}
        p.write_text(json.dumps(data),encoding='utf-8')
        before=p.read_bytes();self.assertEqual(self.run_main('--check','--require-all-ready'),0)
        self.assertEqual(p.read_bytes(),before)

    def test_check_rejects_changed_controller(self):
        self.run_main();self.write('simulations/unit-lab/app.mjs','changed fixture')
        self.assertEqual(self.run_main('--check'),1)
        self.assertIn('frontend_source_changed:simulations/unit-lab/app.mjs',M.collect(self.root)['experiments'][0]['issues'])

    def test_candidate_does_not_count_as_fulltext_read(self):
        self.ref['full_text_status']='candidate'
        self.json('docs/unit-references.json',{'references':[self.ref]})
        result=M.collect(self.root)
        self.assertEqual(result['fulltext_read_reference_count'],0)
        self.assertEqual(result['scientific_ready_count'],0)

    def test_optional_missing_pdf_is_not_reported_as_matched(self):
        path=self.json('local-manifest.json',{'papers':[{'sha256':self.pdfsha,'local_file':'absent.pdf','reading_status':'fulltext_read'}]})
        result=M.collect(self.root,[path])
        self.assertEqual(result['references'][0]['local_pdf_verification']['status'],'not_available')

    def test_optional_pdf_hash_mismatch_invalidates_current_check(self):
        (self.root/'fixture.pdf').write_bytes(b'wrong bytes')
        path=self.json('local-manifest.json',{'papers':[{'sha256':self.pdfsha,'local_file':'fixture.pdf','reading_status':'fulltext_read'}]})
        result=M.collect(self.root,[path])
        self.assertEqual(result['references'][0]['local_pdf_verification']['status'],'mismatch')
        self.assertEqual(result['scientific_ready_count'],0)

    def test_legacy_baseline_uses_verified_registry_and_read_references(self):
        self.entry.update(slug='pendulum');self.entry.pop('frontend_validation')
        self.json('simulations/registry.json',{'experiment_count':1,'simulations':[self.entry]})
        self.assertEqual(M.collect(self.root)['scientific_ready_count'],1)

    def test_check_missing_outputs_writes_nothing(self):
        self.assertEqual(self.run_main('--check'),1)
        self.assertFalse((self.root/'docs/series-scientific-manifest.json').exists())

if __name__=='__main__':unittest.main()
