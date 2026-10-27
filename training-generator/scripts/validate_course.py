#!/usr/bin/env python3
"""Validate honest course structure and catch player-crashing input. Stdlib only."""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

BAD=re.compile(r'\b(?:lorem\s+ipsum|to\s+be\s+written)\b|^\s*(?:tbd|todo|placeholder|lorem(?: ipsum)?|\.\.\.|coming soon)\s*[.!]?\s*$',re.I)
def good(s,minimum=1):
    if not isinstance(s,str) or len(s.split())<minimum or BAD.search(s):return False
    words=re.findall(r'[a-zA-Z]+',s.casefold())
    return not (len(words)>=15 and len(set(words))/len(words)<.30)
def codepart(x):
    return isinstance(x,dict) and x.get('type')=='code'
def textpart(x):
    return x if isinstance(x,str) else x.get('text','') if isinstance(x,dict) else ''
def validate(d):
    issues=[]
    if not isinstance(d,dict): return ['Root must be object'],[]
    if not good(d.get('title')) or not good(d.get('audience')):issues.append('Missing title/audience')
    if d.get('status') not in ('draft','complete'):issues.append('Root status must be draft or complete')
    band=d.get('learner_age_band','adult')
    if band not in ('6-8','adult'):issues.append('learner_age_band must be 6-8 or adult')
    mods=d.get('modules')
    if not isinstance(mods,list) or not mods:return issues+['modules must be nonempty array'],[]
    lessons=[];seen={};complete=0; summaries=[]; allq=[]; resource_sets=[]
    original=[]; ngram_owner=defaultdict(set); code_owner=defaultdict(set); prompt_owner=defaultdict(set)
    lab_owner=defaultdict(set); pitfalls_owner=defaultdict(set); scene_owner=defaultdict(set); lab_sentence_owner=defaultdict(set)
    for mi,m in enumerate(mods):
        if not isinstance(m,dict) or not good(m.get('title')) or not isinstance(m.get('lessons'),list):
            issues.append(f'Module {mi+1}: invalid structure');continue
        for l in m['lessons']:
            lessons.append(l)
            n=len(lessons);p=f'lesson {n}'
            if not isinstance(l,dict):issues.append(f'{p}: must be object');continue
            if not good(l.get('title')):issues.append(f'{p}: missing title')
            status=l.get('status','generated')
            if status=='planned':
                if d.get('status')=='complete':issues.append(f'{p}: planned in complete course')
                continue
            if status not in ('generated','complete'):issues.append(f'{p}: unknown status');continue
            complete+=1
            original.append((n,l))
            for field,minimum in [('hook',30),('challenge',30)]:
                if not good(l.get(field),minimum):issues.append(f'{p}: {field} too short/placeholder (min {minimum} words)')
            for field,minimum in [('objectives',2),('explanation',3),('examples',2),('scenes',3),('questions',3),('pitfalls',1),('resources',0)]:
                v=l.get(field)
                if not isinstance(v,list) or len(v)<minimum:issues.append(f'{p}: {field} must be array of at least {minimum}')
            explanation=l.get('explanation',[])
            if isinstance(explanation,list):
                para=[textpart(x) for x in explanation]
                prose=[textpart(x) for x in explanation if not (isinstance(x,dict) and x.get('type')=='code')]
                if any(not (isinstance(x,str) and good(x)) and not (codepart(x) and isinstance(x.get('text'),str) and not BAD.search(x['text'])) for x in explanation):issues.append(f'{p}: invalid explanation element')
                wc=sum(len(x.split()) for x in prose)
                child=(band=='6-8')
                if wc<(150 if child else 300):issues.append(f'{p}: shallow explanation ({wc} words)')
                summaries.append((l.get('title',''),wc,sum(1 for x in explanation if codepart(x))+sum(1 for ex0 in l.get('examples',[]) if isinstance(ex0,dict) for step in (ex0.get('walkthrough',[]) if isinstance(ex0.get('walkthrough'),list) else [ex0.get('walkthrough')]) if codepart(step)),len(explanation),len(l.get('questions',[])) if isinstance(l.get('questions'),list) else 0))
                signature=' '.join(para).strip()
                for paragraph in prose:
                    tokens=re.findall(r"\b[\w]+\b",paragraph.casefold())
                    for i in range(max(0,len(tokens)-5)):
                        ngram_owner[tuple(tokens[i:i+6])].add(n)
                for block in explanation:
                    if codepart(block) and block.get("text","").strip():code_owner[block["text"].strip()].add(n)
                if signature in seen:issues.append(f'{p}: explanation duplicates lesson {seen[signature]}')
                seen[signature]=n
            ex=l.get('examples',[])
            if isinstance(ex,list):
                for j,x in enumerate(ex):
                    if not isinstance(x,dict) or not good(x.get('title')):issues.append(f'{p}: invalid example {j+1}');continue
                    steps=x.get('walkthrough');steps=steps if isinstance(steps,list) else [steps]
                    for k in steps:
                        if codepart(k) and k.get("text","").strip():code_owner[k["text"].strip()].add(n)
                    if any(not isinstance(k,(str,dict)) or (codepart(k) and (not isinstance(k.get('text'),str) or BAD.search(k['text']))) or (not codepart(k) and not good(textpart(k))) for k in steps) or sum(len(textpart(k).split()) for k in steps if not codepart(k))<80:
                        issues.append(f'{p}: example {j+1} requires >=80 words of worked steps (code excluded)')
            scenes=l.get('scenes',[])
            if isinstance(scenes,list):
                for j,s in enumerate(scenes):
                    if not isinstance(s,dict) or not good(s.get('narration'),5) or not good(s.get('title')) or not isinstance(s.get('visual'),dict):issues.append(f'{p}: invalid scene {j+1}')
            if isinstance(scenes,list):
                scene_owner[tuple(str(k.get("title","")).strip().casefold() for k in scenes if isinstance(k,dict))].add(n)
            lab=l.get('lab')
            if not isinstance(lab,dict) or not good(lab.get('title')) or not good(lab.get('instructions'),30) or not good(lab.get('success'),5):issues.append(f'{p}: invalid lab')
            if isinstance(lab,dict):
                lab_owner[" ".join(str(lab.get("instructions","")).casefold().split())].add(n)
                lab_tokens=re.findall(r"\b[\w]+\b",str(lab.get("instructions","")).casefold())
                for i in range(max(0,len(lab_tokens)-5)):
                    ngram_owner[tuple(lab_tokens[i:i+6])].add(n)
                for sentence in re.split(r'(?<=[.!?])\s+|\n+',str(lab.get("instructions",""))):
                    norm=' '.join(sentence.casefold().split())
                    if len(re.findall(r'\b[\w]+\b',norm))>=8:lab_sentence_owner[norm].add(n)
            pitfalls=l.get("pitfalls",[])
            if isinstance(pitfalls,list):pitfalls_owner[tuple(str(x).strip().casefold() for x in pitfalls)].add(n)
            ca=l.get('practical_application',l.get('corporate_application'))
            if l.get('practical_application') is not None and l.get('corporate_application') is not None:issues.append(f'{p}: use only one application field')
            if ca is not None:
                if not isinstance(ca,dict) or not good(ca.get('scenario_title')) or not good(ca.get('scenario'),150):
                    issues.append(f'{p}: practical_application needs a scenario_title and >=150 substantive words')
                else:
                    # Discourage content duplication, while preserving valid reuse of necessary terms.
                    base=' '.join(textpart(x) for x in l.get('explanation',[]) if not codepart(x))
                    base+=' '+' '.join(str(ex.get('walkthrough','')) for ex in l.get('examples',[]) if isinstance(ex,dict))
                    ctokens=re.findall(r"\b[\w]+\b",ca['scenario'].casefold())
                    btokens=re.findall(r"\b[\w]+\b",base.casefold())
                    bgrams=set(tuple(btokens[i:i+10]) for i in range(max(0,len(btokens)-9)))
                    cgrams=set(tuple(ctokens[i:i+10]) for i in range(max(0,len(ctokens)-9)))
                    if cgrams and len(cgrams & bgrams)/len(cgrams)>.12:
                        issues.append(f'{p}: practical application repeats existing lesson prose')
            qs=l.get('questions',[])
            if isinstance(qs,list):
                for j,q in enumerate(qs):
                    if not isinstance(q,dict):issues.append(f'{p}: question {j+1} not object');continue
                    allq.append(q)
                    if isinstance(q.get("prompt"),str):
                        normalized=" ".join(q["prompt"].casefold().split())
                        title=" ".join(str(l.get("title","")).casefold().split())
                        if title:normalized=normalized.replace(title,"<topic>")
                        prompt_owner[normalized].add(n)
                    c=q.get('choices');a=q.get('answer')
                    if not isinstance(c,list) or len(c)!=4 or not all(good(x) for x in c) or len(set(x.strip().casefold() for x in c if isinstance(x,str)))!=4 or type(a)!=int or not 0<=a<4 or not good(q.get('prompt')) or not good(q.get('reason'),3):issues.append(f'{p}: invalid question {j+1}')
            rs=l.get('resources',[])
            if isinstance(rs,list):
                resource_sets.append((p,tuple(sorted(r.get('url','') for r in rs if isinstance(r,dict)))))
                for j,r in enumerate(rs):
                    if not isinstance(r,dict) or not good(r.get('title')) or not isinstance(r.get('url'),str) or not re.match(r'^https://[^/\s]+',r['url']):issues.append(f'{p}: invalid resource {j+1} (URL shape only)')
    # Cross-lesson integrity gate: fail manufactured courses, not merely identical full paragraphs.
    for n,l in original:
        paragraphs=l.get('explanation',[])
        tokens=[]
        for part in paragraphs if isinstance(paragraphs,list) else []:
            if not codepart(part):tokens.extend(re.findall(r"\b[\w]+\b",textpart(part).casefold()))
        if isinstance(l.get("lab"),dict):
            tokens.extend(re.findall(r"\b[\w]+\b",str(l["lab"].get("instructions","")).casefold()))
        grams=set(tuple(tokens[i:i+6]) for i in range(max(0,len(tokens)-5)))
        if grams:
            shared=sum(bool(ngram_owner[g]-{n}) for g in grams)
            if shared/len(grams)>.20:
                issues.append(f'lesson {n}: repeated explanation/lab word 6-grams across lessons ({shared}/{len(grams)} = {shared/len(grams):.0%}; max 20%)')
        # Duplicate questions within one lesson (option order does not make a new question).
        prompts=[' '.join(q.get('prompt','').casefold().split()) for q in l.get('questions',[]) if isinstance(q,dict)]
        if len(set(prompts))<len(prompts):issues.append(f'lesson {n}: repeated question prompt within lesson')
        normalized_prompts=[]
        for prompt in prompts:
            prompt=re.sub(r'^use the example and choose the correct answer:\s*','',prompt)
            normalized_prompts.append(prompt)
        if len(set(normalized_prompts))<len(normalized_prompts):issues.append(f'lesson {n}: question duplicated by changing preamble/options')
        if band=='6-8':
            for prompt in prompts:
                if any(phrase in prompt for phrase in ['while studying ', 'which strategy helps you learn?', 'what should you explain to a friend after finishing']):
                    issues.append(f'lesson {n}: generic learning-habit question instead of lesson maths')
        lab=l.get('lab',{})
        if isinstance(lab,dict):
            sentences=[]
            for sentence in re.split(r'(?<=[.!?])\s+|\n+',str(lab.get('instructions',''))):
                norm=' '.join(sentence.casefold().split())
                if len(re.findall(r'\b[\w]+\b',norm))>=8:sentences.append(norm)
            if sentences and sum(len(lab_sentence_owner[t]-{n})>0 for t in sentences)/len(sentences)>.35:
                issues.append(f'lesson {n}: repeated lab instructions across lessons')
    for group,owners in code_owner.items():
        if len(owners)>1:issues.append(f'identical code reused in lessons {sorted(owners)}')
    for prompt,owners in prompt_owner.items():
        if len(owners)>1:issues.append(f'templated question reused in lessons {sorted(owners)}: {prompt[:75]}')
    for label, mapping in [('lab instructions',lab_owner),('pitfall set',pitfalls_owner),('scene title sequence',scene_owner)]:
        for value,owners in mapping.items():
            if value and len(owners)>1:issues.append(f'identical {label} across lessons {sorted(owners)}')
    if not lessons:issues.append('No lessons')
    if not complete:issues.append('No generated lessons')
    warnings=[]
    sentence_owners=defaultdict(set)
    for lesson_number,lesson in original:
        blocks=list(lesson.get('explanation',[]))  # never mutate source during checks
        for example in lesson.get('examples',[]):
            w=example.get('walkthrough',[])
            blocks+=w if isinstance(w,list) else [w]
        for block in blocks:
            if codepart(block):continue
            for sentence in re.split(r'(?<=[.!?])\s+|\n+',textpart(block)):
                norm=' '.join(sentence.casefold().split())
                if len(re.findall(r'\b[\w]+\b',norm))>=12:
                    sentence_owners[norm].add(lesson_number)
    for sentence,owners in sentence_owners.items():
        if len(owners)>1:warnings.append(f'verbatim sentence 12+ words shared across lessons {sorted(owners)}: {sentence[:90]}')
    for n,l in original:
        if not str(l.get('evidence_note','')).strip():warnings.append(f'lesson {n}: missing evidence_note')
    for title,wc,code,paras,nq in summaries:
        if band=='adult' and wc<600:warnings.append(f'{title}: near outline depth ({wc} prose words; target 600-900+ where appropriate)')
        if band=='adult' and code==0:warnings.append(f'{title}: no code blocks; verify whether programming example is needed')
    for i in range(len(resource_sets)):
        for j in range(i):
            if resource_sets[i][1] and resource_sets[i][1]==resource_sets[j][1]:warnings.append(f'{resource_sets[i][0]}: identical resources to {resource_sets[j][0]}')
    if len(allq)>=4:
        answers=[q.get('answer') for q in allq if isinstance(q.get('choices'),list) and len(q['choices'])==4 and type(q.get('answer'))==int]
        if answers:
            if len(set(answers))<4:warnings.append('MCQ answer position unused across course')
            longest=sum((lambda lens,answer: lens.count(max(lens))==1 and lens[answer]==max(lens))([len(c) for c in q['choices']],q['answer']) for q in allq if type(q.get('answer'))==int and isinstance(q.get('choices'),list) and len(q['choices'])==4)
            if longest/len(answers)>.40:warnings.append(f'MCQ correct answer is strictly longest in {longest}/{len(answers)} items ({longest/len(answers):.0%}; target <=40%)')
            counts=Counter(answers)
            if max(counts.values())>len(answers)*.38:warnings.append(f'MCQ key position skew: {dict(sorted(counts.items()))}')
    validate.warnings=warnings
    validate.summaries=summaries
    return issues,lessons

if __name__=='__main__':
    d=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')); issues,ls=validate(d)
    print(f'{len(ls)} indexed lessons; '+('PASS' if not issues else 'FAIL'))
    for issue in issues:print(' -',issue)
    for title,wc,code,para,nq in getattr(validate,'summaries',[]):print(f' DEPTH {title}: prose {wc} | code {code} | questions {nq}')
    for warning in getattr(validate,'warnings',[]):print(' WARNING',warning)
    sys.exit(bool(issues))
