#!/usr/bin/env python3
"""Fail-closed release verification. Draft checks structure/provenance; publish requires approvals.
This cannot replace human domain review or browser QA.
"""
import argparse,hashlib,json,re,sys,tempfile
from pathlib import Path
from collections import Counter
from merge_course import merge
from build_course import build
from validate_course import validate,textpart,codepart

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return ' '.join(str(s).casefold().split())
def words(s):return re.findall(r'\b\w+\b',s.casefold())
def main(root,phase,minwords):
    errors=[];warnings=[]
    index=root/'index.json'; statepath=root/'CONTINUE_HERE.json'
    if not index.is_file():return ['index.json missing'],[]
    if not statepath.is_file():return ['CONTINUE_HERE.json missing; cannot claim checkpointed delivery'],[]
    try: state=json.loads(statepath.read_text()); idx=json.loads(index.read_text()); modules=state['modules']
    except (ValueError,KeyError) as e:return ['Malformed index/checkpoint: '+str(e)],[]
    if len(idx.get('modules',[]))!=len(modules):errors.append('Index/checkpoint module count mismatch')
    if state.get('course_title')!=idx.get('title'):errors.append('Index/checkpoint title mismatch')
    expected=[]; module_data=[]
    for i,m in enumerate(modules):
        if i>=len(idx.get('modules',[])):break
        if norm(m.get('title'))!=norm(idx['modules'][i].get('title')):errors.append(f'Module {i+1}: title mismatch')
        status=m.get('status'); path=m.get('artifact')
        if status=='planned':
            if path or m.get('sha256'):errors.append(f'{m["id"]}: planned module has submitted artifact')
            continue
        if status not in ('review_pending','self_verified','review_passed','approved'):
            errors.append(f'{m.get("id")}: unsupported status {status}; repair required');continue
        if not path or not m.get('sha256'):errors.append(f'{m.get("id")}: source/hash missing');continue
        try:
            target=(root/path).resolve();target.relative_to(root.resolve())
            if not target.is_file() or sha(target)!=m['sha256']:raise ValueError('artifact missing or hash mismatch')
            data=json.loads(target.read_text());module_data.append((m,data,target))
            expected.append(target)
            if data.get('title')!=m['title']:errors.append(f'{m["id"]}: artifact module title mismatch')
            if [norm(x.get('title')) for x in data.get('lessons',[])] != [norm(x.get('title')) for x in idx['modules'][i].get('lessons',[])]:errors.append(f'{m["id"]}: lesson index mismatch')
        except (OSError,ValueError,KeyError) as e:errors.append(f'{m.get("id")}: {e}');continue
        if status in ('self_verified','review_passed','approved'):
            path=m.get('self_review')
            try:
                r=json.loads((root/path).read_text())
                if r.get('module_sha256')!=m['sha256'] or r.get('review_type')!='self_adversarial' or r.get('overall')!='pass':raise ValueError('invalid self-review binding')
                checks=r.get('checks',[])
                required={'mathematics','examples','assessment','application','sources','duplication'}
                labels={str(c.get('id',c.get('name',''))).casefold() for c in checks if c.get('result')=='pass' and len(str(c.get('evidence','')))>25}
                if not required.issubset(labels):raise ValueError('weak self-review: need six substantive checks with evidence: '+','.join(sorted(required-labels)))
            except (TypeError,OSError,ValueError) as e:errors.append(f'{m["id"]}: {e}')
        if status in ('review_passed','approved'):
            try:
                r=json.loads((root/m['review']).read_text())
                if r.get('module_sha256')!=m['sha256'] or r.get('verdict')!='pass' or not r.get('reviewer'):raise ValueError('independent PASS missing or hash mismatch')
                if norm(r['reviewer'])==norm(m.get('author','')):raise ValueError('reviewer is author')
            except (TypeError,OSError,ValueError) as e:errors.append(f'{m["id"]}: {e}')
        if phase=='publish' and status!='approved':errors.append(f'{m["id"]}: human approval and independent review needed for publication')
    if phase=='publish':
        if not state.get('publication_approved'):errors.append('Course publication_approved must be true')
        qa=root/'BROWSER_QA.json'
        if not qa.is_file():errors.append('BROWSER_QA.json absent: actual browser evidence required')
        else:
            try:
                report=json.loads(qa.read_text())
                if report.get('result')!='pass' or not report.get('tested_by') or not report.get('evidence'):errors.append('Browser QA incomplete')
            except ValueError:errors.append('Browser QA malformed')
    if not expected:errors.append('No authored modules')
    if not errors:
        with tempfile.TemporaryDirectory() as td:
            merged=Path(td)/'course.json';html=Path(td)/'course.html'
            # Merge canonical sources only; no transformed explanations or forked builders.
            import subprocess
            wrapped=[]
            for m,data,target in module_data:
                w=Path(td)/(m['id']+'-wrapped.json')
                w.write_text(json.dumps({'modules':[data]}),encoding='utf-8')
                wrapped.append(str(w))
            proc=subprocess.run([sys.executable,str(Path(__file__).with_name('merge_course.py')),str(index),*wrapped],capture_output=True,text=True)
            if proc.returncode:errors.append('Canonical merge failed: '+proc.stderr[-600:])
            else:
                merged.write_text(proc.stdout)
                packaged=root/'course.json'
                if not packaged.is_file() or json.loads(packaged.read_text())!=json.loads(proc.stdout):errors.append('course.json differs from canonical merge')
                course=json.loads(proc.stdout)
                issues,_=validate(course);errors.extend(issues)
                for m in course['modules']:
                    for l in m['lessons']:
                        if l.get('status')=='planned':continue
                        title=l.get('title','?')
                        explanation=' '.join(textpart(x) for x in l.get('explanation',[]) if not codepart(x))
                        wc=len(explanation.split()); band=course.get('learner_age_band','adult')
                        if band=='adult' and wc<minwords:errors.append(f'{title}: explanation {wc} < {minwords} words (examples and applications excluded)')
                        baseparts=[textpart(x) for x in l.get('explanation',[]) if not codepart(x)]
                        sample=[]
                        for ex in l.get('examples',[]):
                            w=ex.get('walkthrough',[])
                            sample += [textpart(x) for x in (w if isinstance(w,list) else [w]) if not codepart(x)]
                        # Reject copied worked paragraphs, not harmless terminology overlap.
                        es={norm(z) for z in baseparts if len(words(z))>=45}
                        xs={norm(z) for z in sample if len(words(z))>=45}
                        if es & xs:errors.append(f'{title}: examples copied into explanation')
                        q=l.get('questions',[])
                        if q:
                            longest=sum(len(c['choices'][c['answer']])>max(len(x) for j,x in enumerate(c['choices']) if j!=c['answer']) for c in q)
                            if longest/len(q)>.4:errors.append(f'{title}: longest-correct bias {longest}/{len(q)}')
                            # Sequence a,b,c,d is not a valid balanced key pattern.
                            if len(q)>=4 and [x['answer'] for x in q[:4]] in ([0,1,2,3],[3,2,1,0]):errors.append(f'{title}: predictable key sequence')
                        app=l.get('practical_application',l.get('corporate_application'))
                        if app and len(str(app.get('scenario','')).split())<150:errors.append(f'{title}: application under 150 words')
                if len(course.get('modules',[])) and len([x for x in course['modules'] for l in x['lessons'] if l.get('status')!='planned'])>0:
                    allq=[q for m in course['modules'] for l in m['lessons'] if l.get('status')!='planned' for q in l.get('questions',[])]
                    if allq:
                        n=sum(len(q['choices'][q['answer']])>max(len(x) for j,x in enumerate(q['choices']) if j!=q['answer']) for q in allq)
                        if n/len(allq)>.4:errors.append(f'Course correct-longest bias {n}/{len(allq)}')
                try:
                    build(str(merged),str(html))
                    final=root/'course.html'
                    if not final.is_file() or final.read_bytes()!=html.read_bytes():errors.append('course.html not byte-identical to canonical builder output')
                except Exception as e:errors.append('Canonical player build failure: '+str(e))
    return errors,warnings

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--course',type=Path,required=True);parser.add_argument('--phase',choices=['draft','publish'],default='draft');parser.add_argument('--min-adult-words',type=int,default=600)
    a=parser.parse_args();e,w=main(a.course.resolve(),a.phase,a.min_adult_words)
    for v in e:print('FAIL:',v)
    for v in w:print('WARN:',v)
    print('RELEASE GATE:', 'PASS' if not e else f'FAIL ({len(e)} issue(s))')
    sys.exit(bool(e))
