import json, subprocess, wave
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
SR=48000
T=[0.0, 4.8, 11.4, 20.3, 27.1, 33.3, 42.1, 48.0, 53.1, 62.2, 73.2, 83.4, 94.8, 102.4, 111.0, 117.6]; TOTAL=T[-1]
n=int(SR*TOTAL); t=np.arange(n)/SR
rng=np.random.default_rng(16)
speech=np.zeros(n); fx=np.zeros(n); music=np.zeros(n)
for i in range(15):
    p=ROOT/'audio'/f'v{i}.mp3'
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(p)],text=True))
    sp=max(1,d/(T[i+1]-T[i]-0.45))
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-af',f'atempo={sp:.5f},loudnorm=I=-16:TP=-1.5:LRA=8','-f','f32le','-ac','1','-ar',str(SR),'-'])
    a=np.frombuffer(raw,dtype='<f4').astype(float); k=round((T[i]+0.3)*SR); m=min(len(a),n-k); speech[k:k+m]+=a[:m]
    print(i,'voice',round(len(a)/SR,2),'slot',T[i+1]-T[i],'speed',round(sp,3))
def add(at,s,g):
    k=round(at*SR)
    if k<0: return
    m=min(len(s),n-k)
    if m>0: fx[k:k+m]+=s[:m]*g
def tt(l): return np.arange(int(SR*l))/SR
def env(x,a=0.005): return np.minimum(x/a,1)
def pop(): x=tt(.12); return np.sin(2*np.pi*(500+3000*x)*x)*np.exp(-x*30)
def whoosh(l=.4): x=tt(l); return rng.normal(0,1,len(x))*np.sin(np.pi*x/l)**2*.5
def tick(f=1750): x=tt(.07); return np.sin(2*np.pi*f*x)*np.exp(-x*60)
def buzz(l=.28,f=140): x=tt(l); return np.sign(np.sin(2*np.pi*f*x))*.5*env(x)*np.minimum((l-x)/.03,1)
def errtone(): return np.concatenate([buzz(.16,330),np.zeros(int(SR*.04)),buzz(.22,220)])
def static(l=.5): x=tt(l); return rng.normal(0,1,len(x))*np.exp(-x*5)*(rng.random(len(x))>.4)
def honk(): x=tt(.45); return (np.sign(np.sin(2*np.pi*310*x))+np.sign(np.sin(2*np.pi*392*x)))*.25*env(x,.02)*np.minimum((.45-x)/.08,1)
def beepdeny(): x=tt(.3); return np.sin(2*np.pi*220*x)*np.sign(np.sin(2*np.pi*6*x)+.2)*.6*np.minimum((.3-x)/.02,1)
def powerdown(): x=tt(.9); f=900*np.exp(-x*4)+40; ph=2*np.pi*np.cumsum(f)/SR; return np.sin(ph)*np.exp(-x*2.5)
def zap(): x=tt(.15); return rng.normal(0,1,len(x))*np.exp(-x*25)+np.sin(2*np.pi*2400*x)*np.exp(-x*30)
def rustle(): x=tt(.6); return rng.normal(0,1,len(x))*(rng.random(len(x))>.7)*np.sin(np.pi*x/.6)*.5
def boom(): x=tt(1.0); f=90*np.exp(-x*3)+35; ph=2*np.pi*np.cumsum(f)/SR; return np.sin(ph)*np.exp(-x*3.5)+rng.normal(0,.3,len(x))*np.exp(-x*20)
def ding(f): x=tt(.8); return (np.sin(2*np.pi*f*x)+.4*np.sin(2*np.pi*f*2.76*x)*np.exp(-x*9))*np.exp(-x*5)*env(x,.002)
def thud(): x=tt(.25); return np.sin(2*np.pi*80*x)*np.exp(-x*18)
def chime(f): x=tt(1.2); return np.sin(2*np.pi*f*x)*np.exp(-x*3)*env(x,.01)
def coin(): x=tt(.35); return (np.sin(2*np.pi*1900*x)+np.sin(2*np.pi*2750*x))*np.exp(-x*14)*env(x,.001)
def sweep_up(l=.5): x=tt(l); f=300+1200*(x/l)**2; return np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*x/l)

# scene whooshes + tag pops
for i in range(1,15): add(T[i]-.25,whoosh(.45),.1)
for s in range(1,15): add(T[s]+.15,pop(),.12)
# S1 hook
def riser(l=1.15):
    x = tt(l); f = 80 + 900 * (x / l) ** 2
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (x / l) ** 1.5
add(0.0, boom(), .4); add(0.0, riser(1.15), .14)
for k in range(8): add(0.3 + k * .1, zap(), .06)
for o in (0.45, 0.7, 0.95): add(o, thud(), .55); add(o, ding(1200), .08); add(o, static(.18), .2)
add(1.18, whoosh(.3), .35); add(1.2, boom(), .3)
add(1.45, pop(), .12); add(1.75, pop(), .12); add(1.65, pop(), .1); add(2.5, buzz(.12, 110), .15); add(2.8, pop(), .14)
# S2
add(T[1]+.4,whoosh(.4),.12); add(T[1]+3.0,pop(),.14); add(T[1]+3.6,ding(660),.12); add(T[1]+3.6,pop(),.12)
# S3
add(T[3]+.3,whoosh(.5),.12); add(T[3]+.9,pop(),.1); add(T[3]+1.3,pop(),.1); add(T[3]+2.2,pop(),.1)
add(T[3]+3.4,pop(),.1)
# S3b: whistle, boom, rumble, crack
def whistle(l=.9):
    x = tt(l); f = 2200 - 1500 * (x / l)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (x / l) * .6
def rumble(l=1.6):
    x = tt(l); n0 = rng.normal(0, 1, len(x)); k = np.ones(400) / 400
    return np.convolve(n0, k, mode='same') * 6 * np.exp(-x * 1.8)
add(T[4]+.3,whoosh(.4),.1); add(T[4]+.15,pop(),.12)
add(T[4]+1.0,whistle(.85),.22)
add(T[4]+1.85,boom(),.6); add(T[4]+1.85,static(.35),.35); add(T[4]+1.85,rumble(1.6),.5)
for k in range(8): add(T[4]+2.0+k*.07,tick(300+k*80),.12)
add(T[4]+2.2,zap(),.15); add(T[4]+2.7,whoosh(.9),.2)
add(T[4]+3.4,pop(),.12); add(T[4]+3.9,pop(),.12); add(T[4]+3.9,errtone(),.14)
# S4
add(T[6]+.4,whoosh(.4),.1); add(T[6]+.9,ding(1046.5),.16); add(T[6]+1.6,whoosh(.4),.1); add(T[6]+2.0,thud(),.35); add(T[6]+2.0,errtone(),.12); add(T[6]+2.6,pop(),.12)
# S5
add(T[7]+.4,pop(),.1); add(T[7]+.6,pop(),.1); add(T[7]+1.4,pop(),.14); add(T[7]+1.4,sweep_up(.4),.08); add(T[7]+2.3,ding(523.25),.12)
# S6
for o,f in [(.6,392.0),(2.0,440.0),(3.4,494.0)]: add(T[13]+o,pop(),.12); add(T[13]+o+.5,ding(f),.1)
for o in (1.1,2.5,3.9): add(T[13]+o,tick(1600),.1); add(T[13]+o,pop(),.1)
for o in (1.5,2.9): add(T[13]+o,whoosh(.25),.1)
add(T[13]+4.8,pop(),.1); add(T[13]+5.2,pop(),.1)
# new scenes
add(T[2]+.3,whoosh(.4),.1)
for o in (.5,.9,1.6,2.0): add(T[2]+o,pop(),.12)
add(T[2]+3.2,thud(),.4); add(T[2]+3.2,errtone(),.12)
add(T[5]+.5,pop(),.1); add(T[5]+.8,pop(),.1); add(T[5]+1.5,whoosh(.3),.1); add(T[5]+1.9,pop(),.1); add(T[5]+2.2,pop(),.1)
add(T[5]+3.6,pop(),.12); add(T[5]+3.6,ding(660),.12); add(T[5]+4.6,pop(),.12)
for o in (.4,.9,1.0,2.0,3.6): add(T[8]+o,pop(),.1)
add(T[8]+2.0,buzz(.12,180),.14); add(T[8]+3.6,ding(523),.12); add(T[8]+5.0,pop(),.1)
for k in range(4): add(T[9]+.4+k*.15,pop(),.08)
add(T[9]+1.0,pop(),.1); add(T[9]+1.3,pop(),.1)
for k in range(4): add(T[9]+2.4+k*.4,thud(),.3); add(T[9]+2.4+k*.4,whoosh(.25),.1)
add(T[9]+3.2,pop(),.1); add(T[9]+4.0,errtone(),.14); add(T[9]+5.4,ding(784),.14)
add(T[10]+.5,pop(),.12); add(T[10]+1.0,whoosh(.4),.1); add(T[10]+3.6,pop(),.12); add(T[10]+3.6,ding(660),.12); add(T[10]+4.6,thud(),.3); add(T[10]+4.6,errtone(),.12)
add(T[11]+1.4,pop(),.12); add(T[11]+1.4,ding(1046),.14); add(T[11]+2.8,pop(),.12); add(T[11]+3.4,ding(660),.1); add(T[11]+4.4,pop(),.12); add(T[11]+5.0,errtone(),.14); add(T[11]+6.0,pop(),.1)
for o in (1.4,2.6,3.8): add(T[12]+o,whoosh(.3),.1); add(T[12]+o+.2,pop(),.1)
add(T[12]+.8,pop(),.1)
add(T[14]+2.4,whoosh(.3),.1)

# S7
add(T[14]+.5,whoosh(.4),.1); add(T[14]+1.4,whoosh(.4),.1); add(T[14]+1.8,pop(),.12); add(T[14]+2.4,chime(784),.1); add(T[14]+3.0,chime(988),.1)

# music: dark ambient pad (A minor / F / D minor / E) + slow pulse
chords=[[55,110,164.81,220],[43.65,87.31,130.81,174.61],[73.42,110,146.83,220],[41.2,82.41,123.47,164.81]]
for k in range(int(TOTAL//5)+2):
    a0=k*5; seg=(t>=a0)&(t<a0+5.8)
    if not seg.any(): continue
    x=t[seg]-a0; e=np.minimum(x/1.4,1)*np.minimum(np.maximum(5.8-x,0)/1.2,1)
    for f in chords[k%4]: music[seg]+=e*(np.sin(2*np.pi*f*x)+.35*np.sin(2*np.pi*f*2.005*x))*.02
music+=np.sin(2*np.pi*55*t)*.03*(.5+.5*np.sin(2*np.pi*t*1.0))**2
for b in np.arange(0.5,TOTAL-1,1.0): 
    x=tt(.2); k=round(b*SR); m=min(len(x),n-k); music[k:k+m]+=np.sin(2*np.pi*50*x[:m])*np.exp(-x[:m]*20)*.05
envs=np.convolve(np.abs(speech),np.ones(SR//10)/(SR//10),mode='same'); duck=1-.5*np.clip(envs/.05,0,1)
fade=np.minimum(t/.3,1)*np.minimum((TOTAL-t)/1.0,1)
full=(music*duck+fx+speech*.95)*fade
full=full/max(1,np.abs(full).max()/.95)
st=np.stack([full,full],axis=1)
with wave.open(str(ROOT/'soundtrack.wav'),'wb') as w:
    w.setparams((2,2,SR,0,'NONE','not compressed')); w.writeframes((st*32767).astype('<i2').tobytes())
print('ok',TOTAL)
