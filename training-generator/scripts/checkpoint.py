#!/usr/bin/env python3
"""Portable, offline checkpoint state machine used by chat and CLI hosts."""
import argparse, hashlib, json, os, pathlib, subprocess, sys, tempfile

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=path.parent,prefix='.checkpoint-')
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            json.dump(data,f,indent=2,ensure_ascii=False);f.write('\n');f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def load(root):
    path=root/'CONTINUE_HERE.json'
    if not path.exists():raise ValueError('No checkpoint; run init')
    return json.loads(path.read_text(encoding='utf-8'))

def current(state):
    """First module not yet self-verified; independent review may trail behind."""
    return next((m for m in state['modules'] if m['status'] not in ('self_verified','review_passed','approved')),None)

def select_review(state, module_id):
    for m in state['modules']:
        if m['id']==module_id: return m
    raise ValueError('Unknown module ID')

def verify_artifacts(root,state):
    for m in state['modules']:
        if m['status'] not in ('planned','needs_repair'):
            if not m.get('artifact') or not m.get('sha256') or digest(root/m['artifact'])!=m['sha256']:
                raise ValueError('Submitted module hash changed: '+m['id'])


def normalize_title(s):
    return " ".join(str(s).casefold().split())

def cmd(args):
    root=pathlib.Path(args.course).resolve();statefile=root/'CONTINUE_HERE.json'
    if args.action=='init':
        if statefile.exists():raise ValueError('Checkpoint already exists; refusing overwrite')
        index=json.loads(pathlib.Path(args.index).read_text(encoding='utf-8'))
        modules=index.get('modules') or []
        if not modules:raise ValueError('Index has no modules')
        ms=[{'id':f'm{i+1:02d}','title':m['title'],'status':'planned','artifact':None,'sha256':None,'review':None,'self_review':None,'author':None} for i,m in enumerate(modules)]
        save(root/'index.json',index)
        state={'version':1,'course_title':index.get('title'),'modules':ms,'publication_approved':False,'review_policy':'independent_review_required'}
        save(statefile,state)
    else:
        state=load(root);verify_artifacts(root,state);m=current(state)
        if args.action=='submit':
            if state.get('blocked_by_review'):raise ValueError('A prior module failed independent review; repair it before proceeding')
            if m is None:raise ValueError('All modules self-verified')
            if m['status'] not in ('planned','needs_repair'):raise ValueError('Current module already submitted')
            source=pathlib.Path(args.module).resolve();data=json.loads(source.read_text(encoding='utf-8'))
            # Complete module payloads should have their own distinct lessons. Validate merged course.
            if data.get('title')!=m['title'] or not data.get('lessons'):raise ValueError('Module title or lessons missing/mismatched')
            if any(x.get('status')=='planned' for x in data['lessons']):raise ValueError('Cannot submit incomplete module')
            index=json.loads((root/'index.json').read_text(encoding='utf-8'))
            for im in index['modules']:
                if im['title']==m['title']:
                    if [normalize_title(x['title']) for x in im['lessons']] != [normalize_title(x.get('title','')) for x in data['lessons']]:
                        raise ValueError('Submitted lesson titles differ from planned syllabus; replan required')
                    im['lessons']=data['lessons']
                else:
                    entry=next(k for k in state['modules'] if k['title']==im['title'])
                    if entry['status'] in ('self_verified','review_passed','approved'):
                        approved=json.loads((root/entry['artifact']).read_text(encoding='utf-8'))
                        if digest(root/entry['artifact'])!=entry['sha256']:raise ValueError('Approved module hash changed')
                        im['lessons']=approved['lessons']
            merged=root/'_validate_merged.json';save(merged,index)
            validator=pathlib.Path(__file__).with_name('validate_course.py')
            try: result=subprocess.run([sys.executable,str(validator),str(merged)],capture_output=True,text=True)
            finally:merged.unlink(missing_ok=True)
            if result.returncode:raise ValueError('Validator failed: '+(result.stdout+result.stderr)[-1800:])
            dest=root/'modules'/f"{m['id']}.json";dest.parent.mkdir(parents=True,exist_ok=True)
            tmp=dest.with_suffix('.tmp');tmp.write_bytes(source.read_bytes());os.replace(tmp,dest)
            m.update(status='review_pending',artifact=str(dest.relative_to(root)),sha256=digest(dest),review=None,self_review=None,author=args.author or 'unspecified')
        elif args.action=='selfreview':
            if not m or m['status']!='review_pending':raise ValueError('No submitted module awaiting self-review')
            r=json.loads(pathlib.Path(args.report).read_text(encoding='utf-8'))
            if r.get('module_sha256')!=m['sha256']:raise ValueError('Self-review hash mismatch')
            if r.get('review_type')!='self_adversarial' or r.get('overall')!='pass':raise ValueError('Passing self_adversarial review required')
            if not isinstance(r.get('checks'),list) or not r['checks'] or any(c.get('result') not in ('pass','not_executed') for c in r['checks']) or not any(c.get('result')=='pass' for c in r['checks']):
                raise ValueError('All self-review checks must pass')
            if any(f.get('severity') in ('critical','high','blocking') and not f.get('resolved',False) for f in r.get('findings',[])):
                raise ValueError('Unresolved blocking finding')
            dest=root/'self-reviews'/f"{m['id']}.json";save(dest,r)
            m['self_review']=str(dest.relative_to(root));m['status']='self_verified'
        elif args.action=='review':
            target=select_review(state,args.module_id) if args.module_id else next((x for x in state['modules'] if x['status']=='self_verified'),None)
            if not target or target['status']!='self_verified':raise ValueError('Module must be self_verified to accept independent review')
            review=json.loads(pathlib.Path(args.report).read_text(encoding='utf-8'))
            if review.get('module_sha256')!=target['sha256']:raise ValueError('Review hash mismatch')
            if review.get('verdict') not in ('pass','fail'):raise ValueError('Review verdict must be pass or fail')
            reviewer=str(review.get('reviewer','')).strip().casefold()
            author=str(target.get('author') or '').strip().casefold()
            if reviewer in ('','self','author') or (author not in ('','unspecified') and reviewer==author):
                raise ValueError('Independent reviewer identity required')
            dest=root/'reviews'/f"{target['id']}.json";save(dest,review)
            target['review']=str(dest.relative_to(root))
            target['status']='review_passed' if review['verdict']=='pass' else 'needs_repair'
            if target['status']=='needs_repair' and any(x['status'] in ('self_verified','review_passed','approved') for x in state['modules'][state['modules'].index(target)+1:]):
                # Keep later authored artifacts for repairs but block further advancement.
                state['blocked_by_review']=target['id']
        elif args.action=='approve':
            target=select_review(state,args.module_id) if args.module_id else next((x for x in state['modules'] if x['status']=='review_passed'),None)
            if not target or target['status']!='review_passed':raise ValueError('Independent PASS required before approval')
            if not args.approver:raise ValueError('Human approver required')
            target['status']='approved';target['approved_by']=args.approver
        elif args.action!='status':raise ValueError('Unknown action')
        if args.action!='status':save(statefile,state)
    state=load(root);next_module=current(state)
    print(json.dumps({'course':state['course_title'],'approved':sum(x['status']=='approved' for x in state['modules']),'total':len(state['modules']),'next':next_module,'publication_approved':state['publication_approved']},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['init','status','submit','selfreview','review','approve']);p.add_argument('--course',required=True);p.add_argument('--index');p.add_argument('--module');p.add_argument('--report');p.add_argument('--approver');p.add_argument('--author');p.add_argument('--module-id');a=p.parse_args()
    try:cmd(a)
    except (ValueError,FileNotFoundError,json.JSONDecodeError) as e:print(f'ERROR: {e}',file=sys.stderr);sys.exit(2)
