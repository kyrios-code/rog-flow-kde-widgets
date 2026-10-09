#!/usr/bin/env python3
import json,re,subprocess,sys
FW=["quiet","balanced","performance"]
def run(*args):
 p=subprocess.run(["z13ctl",*args],capture_output=True,text=True,timeout=12)
 if p.returncode: raise RuntimeError((p.stderr or p.stdout).strip()[:300])
 return p.stdout.strip()
def profiles():
 s=run("profile","--list"); found=[]; details={}
 for line in s.splitlines():
  m=re.match(r"^\s*\*?\s*([a-z][a-z0-9-]*)\s{2,}",line)
  if m and m.group(1) not in found:
   found.append(m.group(1))
   details[m.group(1)]=line[m.end():].strip()
 return FW+[n for n in found if n not in FW]
def profile_details():
 output=run("profile","--list"); result={}
 for line in output.splitlines():
  m=re.match(r"^\s*\*?\s*([a-z][a-z0-9-]*)\s{2,}(.*)$",line)
  if m:result[m.group(1)]=m.group(2).strip()
 return result
def status():
 s=run("status"); a=run("autoswitch","--get")
 def get(pattern,text): 
  m=re.search(pattern,text,re.M);return m.group(1).strip() if m else ""
 return {"ok":True,"profiles":profiles(),"details":profile_details(),"active":get(r"Profile:\s*([^\s(]+)",s),
 "ac":get(r"^\s*AC:\s*(.+)$",a),"battery":get(r"^\s*Battery:\s*(.+)$",a),
 "autoswitch":get(r"Autoswitch:\s*(enabled|disabled)",a)=="enabled",
 "temp":get(r"APU:\s*(.+)$",s),"fan":get(r"Fans:\s*(.+)$",s),
 "power":get(r"Power:\s*(.+)$",s),"tdp":get(r"TDP:\s*(.+)$",s),"uv":get(r"UV:\s*(.+)$",s)}
def main(args):
 if not args: return status()
 if args[0]=="profile" and len(args)==2:
  if args[1] not in profiles() or args[1]=="custom":raise ValueError("Invalid profile")
  run("profile","--set",args[1]);return status()
 if args[0]=="lighting" and len(args)==6:
  device,mode,color,brightness,speed=args[1:]
  if device not in ("keyboard","lightbar","all") or mode not in ("static","breathe","cycle","rainbow","strobe") or brightness not in ("off","low","medium","high") or speed not in ("slow","normal","fast") or not re.fullmatch("[0-9A-Fa-f]{6}",color):raise ValueError("Invalid lighting settings")
  run("apply","--device",device,"--mode",mode,"--color",color,"--brightness",brightness,"--speed",speed)
  return {"ok":True,"message":"Lighting applied"}
 raise ValueError("Unsupported command")
try: print(json.dumps(main(sys.argv[1:])))
except Exception as e: print(json.dumps({"ok":False,"error":str(e)}))
