#!/usr/bin/env python3
import json,os,re,subprocess,time
from pathlib import Path

def read(p):
 try:return Path(p).read_text().strip()
 except OSError:return ''
def cmd(*args):
 try:return subprocess.run(args,capture_output=True,text=True,timeout=2).stdout.strip()
 except (OSError,subprocess.TimeoutExpired):return ''
def match(s,p,d='—'):
 m=re.search(p,s);return m.group(1).strip() if m else d
s=cmd('z13ctl','status'); uv=cmd('z13ctl','undervolt','--get')
info=read('/proc/meminfo');total=int(match(info,r'MemTotal:\s+(\d+)','1'));avail=int(match(info,r'MemAvailable:\s+(\d+)',str(total)));used=(total-avail)/1048576
bat=next(iter(Path('/sys/class/power_supply').glob('BAT*')),None)
capacity=read(bat/'capacity') if bat else ''; bstate=read(bat/'status') if bat else 'Unknown'
route=cmd('ip','route','get','1.1.1.1').split();iface=route[route.index('dev')+1] if 'dev' in route else ''
rx=int(read(f'/sys/class/net/{iface}/statistics/rx_bytes') or 0) if iface else 0
tx=int(read(f'/sys/class/net/{iface}/statistics/tx_bytes') or 0) if iface else 0
cache=Path(f'/tmp/hyrule-z13-net-{os.getuid()}.json'); now=time.monotonic()
try:old=json.loads(cache.read_text())
except (OSError,ValueError):old={}
dt=now-old.get('t',now); down=max(0,(rx-old.get('rx',rx))/dt/1024) if dt>0 and old.get('iface')==iface else 0;up=max(0,(tx-old.get('tx',tx))/dt/1024) if dt>0 and old.get('iface')==iface else 0
cache.write_text(json.dumps(dict(t=now,rx=rx,tx=tx,iface=iface)))
stat=list(map(int,read('/proc/stat').splitlines()[0].split()[1:]));idle=stat[3]+stat[4];ct=sum(stat)
cc=Path(f'/tmp/hyrule-z13-cpu-{os.getuid()}.json')
try:prev=json.loads(cc.read_text())
except (OSError,ValueError):prev={}
d=ct-prev.get('total',ct);cpu=round(100*(1-(idle-prev.get('idle',idle))/d)) if d>0 else 0
cc.write_text(json.dumps(dict(total=ct,idle=idle)))
gpu='—';gm='Shared RAM'
for p in Path('/sys/class/drm').glob('card*/device/gpu_busy_percent'):
 if read(p).isdigit():gpu=read(p);break
for p in Path('/sys/class/drm').glob('card*/device/mem_info_vram_used'):
 a=read(p);b=read(str(p).replace('_used','_total'))
 if a.isdigit() and b.isdigit() and int(b)>0:gm=f'{int(a)/1073741824:.1f}/{int(b)/1073741824:.1f} GiB';break
lines=cmd('df','-h','/').splitlines();disk=lines[1].split() if len(lines)>1 else []
swap=next((x.split() for x in cmd('free','-h').splitlines() if x.startswith('Swap:')),[])
freq=read('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq');uptime=float(read('/proc/uptime').split()[0]);
result=dict(cpu=cpu,gpu=gpu,mem=f'{used:.1f}',memDetail=f'{used:.1f}/{total/1048576:.1f} GiB',memPct=round(100*(total-avail)/total),battery=capacity or '—',batteryDetail=f'{bstate} · limit {match(s,r"limit:\s*(\d+)%")}% ',down=round(down,1),up=round(up,1),gpuMemory=gm,biosVram='32 GiB',temp=match(s,r'APU:\s*(\d+)'),fan=match(s,r'Fans:\s*([^,\n]+)'),profile=match(s,r'Profile:\s*([^\n(]+)'),pl1=match(s,r'TDP:\s*(\d+)W'),pl2=match(s,r'(\d+)W\s*\(PL2\)'),pl3=match(s,r'(\d+)W\s*\(PL3\)'),uv=match(uv,r'CPU:\s*(-?\d+)'),uptime=f'{int(uptime//3600)}h {int(uptime//60%60):02d}m',freq=f'{int(freq)/1000000:.2f} GHz' if freq.isdigit() else '—',disk=f'{disk[2]} / {disk[1]} ({disk[4]})' if len(disk)>4 else '—',swap=f'{swap[2]} / {swap[1]}' if len(swap)>2 else '—',kernel=os.uname().release,processes=' · '.join(cmd('ps','-eo','comm=,pcpu=','--sort=-pcpu').splitlines()[:3]))
print(json.dumps(result))
