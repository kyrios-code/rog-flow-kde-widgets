#!/usr/bin/env python3
"""Read local Steam library, launch installed Gamescope session; no shell or sudo."""
import json, os, pathlib, re, subprocess, sys, shutil
HOME=pathlib.Path.home()
STEAM=[HOME/".local/share/Steam",HOME/".steam/steam",HOME/".var/app/com.valvesoftware.Steam/.local/share/Steam"]
def roots():
    seen=set()
    for p in STEAM:
        if p.exists():
            resolved=p.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield resolved

STEAM_TOOL_NAME = re.compile(
    r"^(?:Proton(?: Experimental| Hotfix| [0-9][\\w. -]*)?|"
    r"Steam Linux Runtime(?:[ -].*)?|"
    r"Steamworks Common Redistributables|"
    r"Steam Runtime(?:[ -].*)?|"
    r"Steam Controller Configs)$", re.I
)

def is_game(name):
    return not STEAM_TOOL_NAME.fullmatch(name.strip())

def library():
    games={}
    for root in roots():
        paths=[root/"steamapps"]
        f=root/"config/libraryfolders.vdf"
        if not f.exists():f=root/"steamapps/libraryfolders.vdf"
        if f.exists():
            raw=f.read_text(errors="replace")
            for path in re.findall(r'"path"\s+"([^"]+)"',raw):
                paths.append(pathlib.Path(path.replace("\\\\","/"))/"steamapps")
        for folder in paths:
            for manifest in folder.glob("appmanifest_*.acf"):
                raw=manifest.read_text(errors="replace")
                appid=re.search(r'"appid"\s+"(\d+)"',raw)
                name=re.search(r'"name"\s+"([^"]+)"',raw)
                if appid and name and is_game(name.group(1)): games[appid.group(1)]=name.group(1)
    return games
def last_played_by_app(raw):
    """Parse LastPlayed within each app's VDF object, not neighboring blocks."""
    tokens=re.findall(r'"(?:\\.|[^"\\])*"|[{}]', raw)
    stack=[]
    pending=None
    result={}
    i=0
    while i<len(tokens):
        token=tokens[i]
        if token=="{":
            stack.append(pending)
            pending=None
        elif token=="}":
            if stack:stack.pop()
            pending=None
        elif token.startswith('"'):
            value=token[1:-1]
            if i+1<len(tokens) and tokens[i+1]=="{":
                pending=value
            elif i+1<len(tokens) and tokens[i+1].startswith('"'):
                next_value=tokens[i+1][1:-1]
                if value.lower()=="lastplayed" and stack and stack[-1] and stack[-1].isdigit() and next_value.isdigit():
                    appid=stack[-1]
                    result[appid]=max(result.get(appid,0),int(next_value))
                i+=1
        i+=1
    return result

def recent(games):
    found={}
    for root in roots():
        for p in (root/"userdata").glob("*/config/localconfig.vdf"):
            for appid,timestamp in last_played_by_app(p.read_text(errors="replace")).items():
                if appid in games:
                    found[appid]=max(found.get(appid,0),timestamp)
    result=[]
    for appid,timestamp in sorted(found.items(),key=lambda item:-item[1])[:5]:
        art=""
        for root in roots():
            cache=root/"appcache/librarycache"
            for candidate in (
                cache/f"{appid}_library_600x900.jpg",
                cache/f"{appid}_library_600x900.png",
                cache/appid/"library_600x900.jpg",
                cache/appid/"library_600x900.png",
                cache/appid/"library_600x900.webp",
            ):
                if candidate.is_file():
                    art=candidate.resolve().as_uri()
                    break
            if art:break
        result.append(dict(id=appid,name=games[appid],lastPlayed=timestamp,art=art))
    return result

def profiles():
    p=subprocess.run(["z13ctl","profile","--list"],capture_output=True,text=True,timeout=12)
    if p.returncode:raise RuntimeError("Could not read profiles")
    names=["quiet","balanced","performance"]
    for line in p.stdout.splitlines():
        m=re.match(r"^\s*\*?\s*([a-z][a-z0-9-]*)\s{2,}",line)
        if m and m.group(1) not in names and m.group(1)!="custom":names.append(m.group(1))
    return names
def profile_details():
    result={}
    p=subprocess.run(["z13ctl","profile","--list"],capture_output=True,text=True,timeout=12)
    if p.returncode:return result
    for line in p.stdout.splitlines():
        m=re.match(r"^\s*\*?\s*([a-z][a-z0-9-]*)\s{2,}(.*)$",line)
        if m:result[m.group(1)]=m.group(2).strip()
    return result

def launch(mode):
    if mode not in profiles():raise ValueError("Profile unavailable")
    if not shutil.which("steamos-session-select"):
        raise RuntimeError("steamos-session-select missing; no session change made")
    r=subprocess.run(["z13ctl","profile","--set",mode],capture_output=True,text=True,timeout=20)
    if r.returncode:raise RuntimeError("Profile switch failed: "+(r.stderr or r.stdout)[:250])
    active=subprocess.run(["z13ctl","profile","--get"],capture_output=True,text=True,timeout=12)
    if active.returncode or mode not in active.stdout:
        raise RuntimeError("Profile not confirmed; Gaming Mode not launched")
    subprocess.Popen(["steamos-session-select","gamescope"],stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
    return {"ok":True,"message":"Switching to Gaming Mode: "+mode}
def controllers():
    """Return connected BlueZ game controllers only; never invent battery values."""
    if not shutil.which("bluetoothctl"):return []
    try:
        p=subprocess.run(["bluetoothctl","devices","Connected"],capture_output=True,text=True,timeout=8)
        if p.returncode:return []
        result=[]
        for line in p.stdout.splitlines():
            m=re.match(r"^Device ([0-9A-Fa-f:]{17}) (.+)$",line.strip())
            if not m:continue
            mac,name=m.groups()
            detail=subprocess.run(["bluetoothctl","info",mac],capture_output=True,text=True,timeout=8).stdout
            # Filter using Bluetooth icon/name and gamepad input UUID where available.
            if not re.search(r"controller|gamepad|joypad|xbox|dualshock|dualsense|8bitdo|pro controller",name,re.I) and not re.search(r"Human Interface Device",detail,re.I):
                continue
            battery=re.search(r"Battery Percentage:\s*(?:0x[0-9a-fA-F]+\s*\()?([0-9]{1,3})\)?",detail)
            pct=int(battery.group(1)) if battery else None
            result.append({"name":name,"mac":mac,"battery":pct if pct is not None and 0<=pct<=100 else None})
            if len(result)>=4:break
        return result
    except (subprocess.TimeoutExpired,OSError):return []

def info():
    games=library()
    result={"ok":True,"installed":len(games),"recent":recent(games),"steamFound":any(True for _ in roots()),"controllers":controllers()}
    try:
        result["profiles"]=profiles()
        result["details"]=profile_details()
        p=subprocess.run(["z13ctl","profile","--get"],capture_output=True,text=True,timeout=10)
        result["active"]=p.stdout.strip() if p.returncode==0 else ""
    except Exception:result["profiles"]=[];result["active"]=""
    return result
try:
    args=sys.argv[1:]
    result=info() if not args else launch(args[1]) if len(args)==2 and args[0]=="launch" else {"ok":False,"error":"Invalid command"}
    print(json.dumps(result))
except Exception as e:print(json.dumps({"ok":False,"error":str(e)}))
