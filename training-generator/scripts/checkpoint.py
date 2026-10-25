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

def normalize_title(s):
    return " ".join(str(s).casefold().split())

def target(state,module_id,states):
    matches=[m for m in state["modules"] if (m["id"]==module_id if module_id else m["status"] in states)]
    if not matches or matches[0]["status"] not in states:raise ValueError("No eligible module")
    return matches[0]

def verify(root,state):
    for m in state["modules"]:
        if m["status"] in ("review_pending","self_verified","review_passed","approved"):
            if not m.get("artifact") or not (root/m["artifact"]).exists() or sha(root/m["artifact"])!=m["sha256"]:
                raise ValueError("Module content hash changed: "+m["id"])

def run(a):
    root=pathlib.Path(a.course).resolve(); statepath=root/"CONTINUE_HERE.json"
    if a.action=="init":
        if statepath.exists():raise ValueError("Course already initialized")
        idx=json.loads(pathlib.Path(a.index).read_text())
        if not idx.get("modules"):raise ValueError("Missing modules")
        save(root/"index.json",idx)
        save(statepath,{"version":1,"course_title":idx.get("title"),"publication_approved":False,
            "modules":[{"id":f"m{i+1:02d}","title":m["title"],"status":"planned","artifact":None,"sha256":None,"review":None,"self_review":None,"author":None} for i,m in enumerate(idx["modules"])]})
    else:
        if not statepath.exists():raise ValueError("No checkpoint: run init")
        s=json.loads(statepath.read_text());verify(root,s);m=next((m for m in s["modules"] if m["status"] not in ("self_verified","review_passed","approved")),None)
        if a.action=="submit":
            if m is None or m["status"] not in ("planned","needs_repair"):raise ValueError("No editable module")
            data=json.loads(pathlib.Path(a.module).read_text())
            if data.get("title")!=m["title"] or not data.get("lessons") or any(x.get("status")=="planned" for x in data["lessons"]):raise ValueError("Module missing, mismatched or incomplete")
            idx=json.loads((root/"index.json").read_text())
            for mod in idx["modules"]:
                old=next(k for k in s["modules"] if k["title"]==mod["title"])
                if old["id"]==m["id"]:
                    planned=[normalize_title(x["title"]) for x in mod["lessons"]]
                    submitted=[normalize_title(x.get("title","")) for x in data["lessons"]]
                    if planned!=submitted:raise ValueError("Submitted lesson titles differ from planned syllabus; explicit replan required")
                    mod["lessons"]=data["lessons"]
                elif old["status"] in ("self_verified","review_passed","approved"):
                    p=root/old["artifact"]
                    if sha(p)!=old["sha256"]:raise ValueError("Approved content hash changed")
                    mod["lessons"]=json.loads(p.read_text())["lessons"]
            tmp=root/"_merged_for_validation.json";save(tmp,idx)
            try:
                v=pathlib.Path(__file__).with_name("validate_course.py")
                result=subprocess.run([sys.executable,str(v),str(tmp)],capture_output=True,text=True)
            finally:tmp.unlink(missing_ok=True)
            if result.returncode:raise ValueError("Validation failed: "+(result.stdout+result.stderr)[-1500:])
            dest=root/"modules"/(m["id"]+".json");dest.parent.mkdir(parents=True,exist_ok=True);temp=dest.with_suffix(".tmp");temp.write_bytes(pathlib.Path(a.module).read_bytes());os.replace(temp,dest)
            m.update(status="review_pending",artifact=str(dest.relative_to(root)),sha256=sha(dest),review=None,self_review=None,author=a.author or "unspecified")
        elif a.action=="selfreview":
            t=target(s,None,("review_pending",))
            r=json.loads(pathlib.Path(a.report).read_text())
            if r.get("module_sha256")!=t["sha256"] or r.get("review_type")!="self_adversarial" or r.get("overall")!="pass":
                raise ValueError("Matching passing self-adversarial report required")
            checks=r.get("checks")
            if not isinstance(checks,list) or not checks or not any(x.get("result")=="pass" for x in checks) or any(x.get("result") not in ("pass","not_executed") for x in checks):
                raise ValueError("Self-review checks missing or failed")
            if any(x.get("severity") in ("critical","high","blocking") and not x.get("resolved",False) for x in r.get("findings",[])):
                raise ValueError("Blocking self-review finding")
            dest=root/"self-reviews"/(t["id"]+".json");save(dest,r)
            t["self_review"]=str(dest.relative_to(root));t["status"]="self_verified"
        elif a.action=="review":
            t=target(s,a.module_id,("self_verified",))
            r=json.loads(pathlib.Path(a.report).read_text())
            if r.get("module_sha256")!=t["sha256"] or r.get("verdict") not in ("pass","fail"):
                raise ValueError("Review hash or verdict invalid")
            reviewer=str(r.get("reviewer","")).strip().casefold()
            if reviewer in ("","self","author") or (t.get("author") not in (None,"unspecified") and reviewer==t["author"].strip().casefold()):
                raise ValueError("Reviewer must differ from author")
            dest=root/"reviews"/(t["id"]+".json");save(dest,r)
            t["review"]=str(dest.relative_to(root));t["status"]="review_passed" if r["verdict"]=="pass" else "needs_repair"
        elif a.action=="approve":
            t=target(s,a.module_id,("review_passed",))
            if not a.approver:raise ValueError("Human approver required")
            t["status"]="approved";t["approved_by"]=a.approver
        elif a.action!="status":raise ValueError("Unknown action")
        if a.action!="status":save(statepath,s)
    s=json.loads(statepath.read_text());n=next((m for m in s["modules"] if m["status"] not in ("self_verified","review_passed","approved")),None)
    print(json.dumps({"course":s["course_title"],"approved":sum(m["status"]=="approved" for m in s["modules"]),"total":len(s["modules"]),"next":n},indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("action",choices=["init","status","submit","selfreview","review","approve"])
    p.add_argument("--course",required=True);p.add_argument("--index");p.add_argument("--module");p.add_argument("--report");p.add_argument("--approver");p.add_argument("--author");p.add_argument("--module-id")
    try:run(p.parse_args())
    except (ValueError,OSError,json.JSONDecodeError) as e:print("ERROR:",e,file=sys.stderr);sys.exit(2)
