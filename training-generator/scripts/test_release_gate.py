#!/usr/bin/env python3
"""Adversarial regression suite: every corrupted fixture must be rejected."""
import json,tempfile,unittest,sys,hashlib
from pathlib import Path
from release_gate import main
from build_course import build
from merge_course import merge
from validate_course import validate

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        example=Path(__file__).resolve().parent.parent/'references/example-lesson.json'
        data=json.loads(example.read_text());data['modules']=data['modules'][:1]
        data['modules'][0]['lessons']=data['modules'][0]['lessons'][:1]
        lesson=data['modules'][0]['lessons'][0];lesson['questions'][0]['choices'][lesson['questions'][0]['answer']]='Okay'
        # Existing specimen is intentionally imperfect; modify only the fixture's test questions.
        for i,q in enumerate(lesson['questions']):
            q['answer']=([2,0,3,1][i%4]);q['choices']=[f'Candidate alternative {j} for evaluation' for j in range(4)]
            q['choices'][q['answer']]='Selected interpretation'
        self.lesson=lesson;self.index=json.loads(json.dumps(data));self.index['modules'][0]['lessons']=[{'title':lesson['title'],'status':'planned'}]
        (self.root/'index.json').write_text(json.dumps(self.index))
        (self.root/'modules').mkdir();self.module=self.root/'modules/m01.json';self.module.write_text(json.dumps(data['modules'][0]))
        (self.root/'CONTINUE_HERE.json').write_text(json.dumps({'course_title':data['title'],'modules':[{'id':'m01','title':data['modules'][0]['title'],'status':'review_pending','artifact':'modules/m01.json','sha256':sha(self.module)}],'publication_approved':False}))
        full=merge(self.index,[{'modules':[data['modules'][0]]}]);(self.root/'course.json').write_text(json.dumps(full));build(self.root/'course.json',self.root/'course.html')
    def tearDown(self):self.tmp.cleanup()
    def test_good_draft(self):
        errors,_=main(self.root,'draft',300)
        self.assertFalse(errors,errors)
    def test_validator_is_pure(self):
        before=(self.root/'course.json').read_text()
        data=json.loads(before); snapshot=json.dumps(data,sort_keys=True)
        validate(data)
        self.assertEqual(json.dumps(data,sort_keys=True),snapshot)
    def test_missing_checkpoint(self):
        (self.root/'CONTINUE_HERE.json').unlink();errors,_=main(self.root,'draft',300);self.assertTrue(any('CONTINUE_HERE' in x for x in errors))
    def test_stale_module_hash(self):
        self.module.write_text(self.module.read_text()+' ');errors,_=main(self.root,'draft',300);self.assertTrue(any('hash mismatch' in x for x in errors))
    def test_changed_merged_json(self):
        p=self.root/'course.json';data=json.loads(p.read_text());data['description']='Unreviewed change';p.write_text(json.dumps(data));errors,_=main(self.root,'draft',300);self.assertTrue(any('canonical merge' in x for x in errors))
    def test_changed_html(self):
        p=self.root/'course.html';p.write_text(p.read_text()+'<!-- tampered -->');errors,_=main(self.root,'draft',300);self.assertTrue(any('byte-identical' in x for x in errors))
    def test_publish_without_review(self):
        errors,_=main(self.root,'publish',300);self.assertTrue(any('approval' in x for x in errors))
    def test_duplicate_example(self):
        d=json.loads(self.module.read_text());ex=d['lessons'][0]['examples'][0]['walkthrough'];piece=ex[0] if isinstance(ex,list) else ex
        d['lessons'][0]['explanation'].append(piece)
        self.module.write_text(json.dumps(d));state=json.loads((self.root/'CONTINUE_HERE.json').read_text());state['modules'][0]['sha256']=sha(self.module);(self.root/'CONTINUE_HERE.json').write_text(json.dumps(state));
        full=merge(self.index,[{'modules':[d]}]);(self.root/'course.json').write_text(json.dumps(full));build(self.root/'course.json',self.root/'course.html')
        errors,_=main(self.root,'draft',300);self.assertTrue(any('copied' in x for x in errors),errors)
if __name__=='__main__':unittest.main()
