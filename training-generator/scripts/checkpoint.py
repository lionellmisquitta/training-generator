#!/usr/bin/env python3
"""Portable module checkpoint manager. Standard-library only; no model API."""
import argparse, hashlib, json, os, pathlib, sys, tempfile, subprocess

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=p.parent,prefix=".checkpoint-")
    try:
        with os.fdopen(fd,"w",encoding="utf8") as f:
            json.dump(obj,f,indent=2,ensure_ascii=False)
            f.write("\n");f.flush();os.fsync(f.fileno())
        os.replace(tmp,p)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def run(a):
    root=pathlib.Path(a.course).resolve(); statepath=root/"CONTINUE_HERE.json"
    if a.action=="init":
        if statepath.exists():raise ValueError("Course already initialized")
        idx=json.loads(pathlib.Path(a.index).read_text())
        if not idx.get("modules"):raise ValueError("Missing modules")
        save(root/"index.json",idx)
        save(statepath,{"version":1,"course_title":idx.get("title"),"publication_approved":False,
            "modules":[{"id":f"m{i+1:02d}","title":m["title"],"status":"planned","artifact":None,"sha256":None,"review":None} for i,m in enumerate(idx["modules"])]})
    else:
        if not statepath.exists():raise ValueError("No checkpoint: run init")
        s=json.loads(statepath.read_text());m=next((m for m in s["modules"] if m["status"]!="approved"),None)
        if a.action=="submit":
            if m is None or m["status"] not in ("planned","needs_repair"):raise ValueError("No editable module")
            data=json.loads(pathlib.Path(a.module).read_text())
            if data.get("title")!=m["title"] or not data.get("lessons") or any(x.get("status")=="planned" for x in data["lessons"]):raise ValueError("Module missing, mismatched or incomplete")
            idx=json.loads((root/"index.json").read_text())
            for mod in idx["modules"]:
                old=next(k for k in s["modules"] if k["title"]==mod["title"])
                if old["id"]==m["id"]:mod["lessons"]=data["lessons"]
                elif old["status"]=="approved":
                    p=root/old["artifact"]
                    if sha(p)!=old["sha256"]:raise ValueError("Approved content hash changed")
                    mod["lessons"]=json.loads(p.read_text())["lessons"]
            tmp=root/"_merged_for_validation.json";save(tmp,idx)
            try:
                v=pathlib.Path(__file__).with_name("validate_course.py")
                result=subprocess.run([sys.executable,str(v),str(tmp)],capture_output=True,text=True)
            finally:tmp.unlink(missing_ok=True)
            if result.returncode:raise ValueError("Validation failed: "+(result.stdout+result.stderr)[-1500:])
            dest=root/"modules"/(m["id"]+".json");save(dest,data)
            m.update(status="review_pending",artifact=str(dest.relative_to(root)),sha256=sha(dest),review=None)
        elif a.action=="review":
            if not m or m["status"]!="review_pending":raise ValueError("No module awaiting review")
            review=json.loads(pathlib.Path(a.report).read_text())
            if review.get("module_sha256")!=m["sha256"]:raise ValueError("Review is not for this module hash")
            if review.get("verdict") not in ("pass","fail") or not review.get("reviewer") or review["reviewer"] in ("author","self"):raise ValueError("Independent review metadata missing")
            dest=root/"reviews"/(m["id"]+".json");save(dest,review)
            m["review"]=str(dest.relative_to(root));m["status"]="review_passed" if review["verdict"]=="pass" else "needs_repair"
        elif a.action=="approve":
            if not m or m["status"]!="review_passed" or not a.approver:raise ValueError("Independent PASS and human approver required")
            m["status"]="approved";m["approved_by"]=a.approver
        elif a.action!="status":raise ValueError("Unknown action")
        if a.action!="status":save(statepath,s)
    s=json.loads(statepath.read_text());n=next((m for m in s["modules"] if m["status"]!="approved"),None)
    print(json.dumps({"course":s["course_title"],"approved":sum(m["status"]=="approved" for m in s["modules"]),"total":len(s["modules"]),"next":n},indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("action",choices=["init","status","submit","review","approve"])
    p.add_argument("--course",required=True);p.add_argument("--index");p.add_argument("--module");p.add_argument("--report");p.add_argument("--approver")
    try:run(p.parse_args())
    except (ValueError,OSError,json.JSONDecodeError) as e:print("ERROR:",e,file=sys.stderr);sys.exit(2)
