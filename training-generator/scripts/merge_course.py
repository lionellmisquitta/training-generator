#!/usr/bin/env python3
"""Merge generated module lessons into a planned index by exact module and lesson title."""
import json,sys
from pathlib import Path
from validate_course import validate

def norm(s):return ' '.join(s.strip().casefold().split())
def merge(master,parts):
    out=json.loads(json.dumps(master))
    for part in parts:
        for module in part.get('modules',[]):
            targets=[m for m in out['modules'] if norm(m['title'])==norm(module['title'])]
            if len(targets)!=1:raise ValueError('Unknown or duplicate module: '+module['title'])
            for lesson in module['lessons']:
                slots=[i for i,l in enumerate(targets[0]['lessons']) if norm(l['title'])==norm(lesson['title'])]
                if len(slots)!=1:raise ValueError('Unknown or duplicate lesson: '+lesson['title'])
                if lesson.get('status')=='planned':continue
                old=targets[0]['lessons'][slots[0]]
                if old.get('status')!='planned' and old!=lesson:raise ValueError('Conflicting generated lesson: '+lesson['title'])
                targets[0]['lessons'][slots[0]]=lesson
    if out.get('status')=='complete' and any(l.get('status')=='planned' for m in out['modules'] for l in m['lessons']):raise ValueError('Complete course has planned lessons')
    errors,_=validate(out)
    if errors:raise ValueError('; '.join(errors))
    return out
if __name__=='__main__':
    if len(sys.argv)<3:sys.exit('Usage: merge_course.py index.json module1.json [module2.json ...] > course.json')
    d=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
    print(json.dumps(merge(d(sys.argv[1]),[d(p) for p in sys.argv[2:]]),ensure_ascii=False,indent=2))
