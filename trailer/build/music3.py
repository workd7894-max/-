import numpy as np, wave, scipy.signal as ss
np.random.seed(7)
SR=44100; BPM=120; B=60/BPM; T=50.0; N=int(SR*T)
bus={k:np.zeros((N,2)) for k in ['drum','mus','fx']}
def add(sig,st,pan=0.0,g=1.0,b='mus'):
    i=int(st*SR)
    if i>=N: return
    j=min(N,i+len(sig)); s=sig[:j-i]*g
    bus[b][i:j,0]+=s*(1-pan); bus[b][i:j,1]+=s*(1+pan)
def lpf(x,fc,o=2): b,a=ss.butter(o,min(fc/(SR/2),0.99)); return ss.lfilter(b,a,x)
def hpf(x,fc,o=2): b,a=ss.butter(o,fc/(SR/2),'high'); return ss.lfilter(b,a,x)
def bpf(x,lo,hi): b,a=ss.butter(2,[lo/(SR/2),hi/(SR/2)],'band'); return ss.lfilter(b,a,x)
def tt(d): return np.arange(int(d*SR))/SR
def nf(m): return 440*2**((m-69)/12)
def saws(f,d,voices=5,spread=0.012,vib=0):
    t=tt(d); s=0
    for k in range(voices):
        det=1+spread*(k-(voices-1)/2)/max(1,(voices-1)/2)
        ph=np.random.rand()
        fm=f*det*(1+vib*0.004*np.sin(2*np.pi*5.2*t+k))
        s=s+2*((np.cumsum(fm)/SR+ph)%1)-1
    return s/voices
def adsr(n,a,d,s,r):
    e=np.ones(n)*s; A=min(int(a*SR),n//3); D=int(d*SR); R=min(int(r*SR),n//3)
    e[:A]=np.linspace(0,1,A) if A else e[:A]
    e[A:A+D]=np.linspace(1,s,len(e[A:A+D]))
    if R: e[-R:]*=np.linspace(1,0,R)
    return e
# --- instruments
def taiko(g=1.0,big=False):
    t=tt(1.6 if big else 0.9); f=(52 if big else 68)+90*np.exp(-t*25)
    body=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*(3 if big else 6))
    skin=lpf(np.random.randn(len(t)),900)*np.exp(-t*30)*0.6
    return np.tanh(2.2*(body+skin))*g
def ka():
    t=tt(0.08); return bpf(np.random.randn(len(t)),2000,6000)*np.exp(-t*60)*0.5
def brass(notes,d,swell=0.4):
    n=int(d*SR); x=sum(saws(nf(m),d,5,0.01) for m in notes)/len(notes)
    dark=lpf(x,500); bright=lpf(x,2600)
    e=adsr(n,swell,0.3,0.8,0.3); k=np.clip(e,0,1)**1.5
    return np.tanh(1.6*(dark*(1-k)+bright*k))*e
def braam(notes,d=2.5):
    n=int(d*SR); x=sum(saws(nf(m),d,7,0.02) for m in notes)/len(notes)
    e=adsr(n,0.02,0.4,0.7,1.2)
    bright=lpf(x,1800); dark=lpf(x,300); k=np.exp(-tt(d)*1.5)
    sub=np.sin(2*np.pi*nf(notes[0]-12)*tt(d))*np.exp(-tt(d)*1.2)
    return np.tanh(2.5*(bright*k+dark*(1-k)+0.8*sub))*e
def string16(m,dur):
    x=saws(nf(m),dur,5,0.008); x=lpf(hpf(x,200),3200)
    return x*adsr(len(x),0.004,0.08,0.3,0.03)
def choir(notes,d):
    t=tt(d); out=0
    for m in notes:
        f=nf(m)*(1+0.005*np.sin(2*np.pi*5*t+np.random.rand()*6))
        ph=2*np.pi*np.cumsum(f)/SR
        for h in range(1,14):
            fh=nf(m)*h; w=np.exp(-((fh-700)/250)**2)+0.7*np.exp(-((fh-1150)/300)**2)+0.25*np.exp(-((fh-2600)/400)**2)+0.15/h
            out=out+w*np.sin(h*ph)
    out=out/len(notes)
    return out*adsr(len(t),0.6,0.5,0.85,0.8)
def boom(g=1.0):
    t=tt(3.0); f=30+80*np.exp(-t*6)
    return np.tanh(2*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*1.3))*g
def riser(st,d,g=0.3):
    t=tt(d); k=t/d; nz=np.random.randn(len(t)); out=np.zeros(len(t)); seg=int(0.04*SR)
    for i in range(0,len(t),seg):
        c=300+9000*k[i]**2; out[i:i+seg]=bpf(nz[i:i+seg+0],c*0.6,min(c*1.4,20000))[:len(out[i:i+seg])]
    tone=saws(1,d,3,0.03)*0  # placeholder
    sw=np.sin(2*np.pi*np.cumsum(110+880*k**2)/SR)*0.25
    add((out+sw)*k**2,st,0,g,'fx')
def whoosh(st,g=0.25):
    t=tt(0.6); k=np.sin(np.pi*t/0.6); add(bpf(np.random.randn(len(t)),800,5000)*k,st-0.3,0,g,'fx')
# --- harmony: Dm Bb F C / Dm Bb Gm A  (2s per chord)
P=[(50,[62,65,69]),(46,[58,62,65]),(41,[57,60,65]),(48,[55,60,64]),
   (50,[62,65,69]),(46,[58,62,65]),(43,[55,58,62]),(45,[57,61,64])]
osti=[0,12,7,12, 3,12,7,12, 0,12,7,12, 3,12,7,15]  # relative pattern over chord root
for bar in range(25):
    st=bar*4*B; root,ch=P[bar%8]; d=4*B
    # low drone/choir always (quieter in drop)
    if st<44:
        add(choir([c-12 for c in ch],d+0.6),st,0,0.18 if st<30 else 0.14)
    if st<8:
        add(lpf(saws(nf(root-12),d+0.3,5,0.01),250)*adsr(int((d+0.3)*SR),1.0,0.1,1,0.4),st,0,0.35)
    if 8<=st<44:
        # strings ostinato 16ths
        step=B/4
        for k in range(16):
            m=root+12+osti[k]+(12 if st>=30 else 0)
            add(string16(m,step*0.95),st+k*step,0.35 if k%2 else -0.35,0.16 if st<18 else 0.2)
        # low brass sustain
        add(brass([root-12,root-5,root],d,0.6 if st<30 else 0.15),st,0,0.28 if st<30 else 0.34)
    if 30<=st<44:
        # heroic brass melody (top voice)
        mel=[ch[2]+12,ch[1]+12,ch[2]+12,ch[0]+12+2]
        for i,m in enumerate([ch[2],ch[1]+12-12,ch[2],ch[0]+2]):
            pass
        line=[ch[0]+12,ch[1]+12,ch[2]+12,ch[1]+12]
        durs=[1.5*B,0.5*B,1.5*B,0.5*B]; tpos=st
        for m,dd in zip(line,durs):
            add(brass([m-12,m-5,m],dd*1.05,0.05),tpos,0,0.22); tpos+=dd
# --- drums
for i in range(100):
    t=i*B
    if 8<=t<18:
        if i%4==0: add(taiko(0.8,True),t,0,1,'drum')
        if i%4==2: add(taiko(0.5),t,0.2,1,'drum')
    elif 18<=t<30:
        add(taiko(0.75,i%2==0),t,0,1,'drum')
        add(taiko(0.4),t+B*0.75,-0.3,1,'drum')
        add(ka(),t+B/2,0.4,0.8,'drum')
    elif 30<=t<40:
        add(taiko(1.0,True),t,0,1,'drum')
        add(taiko(0.5),t+B/2,0.25,1,'drum'); add(taiko(0.4),t+B*0.75,-0.25,1,'drum')
        add(ka(),t+B/4,0.4,0.7,'drum'); add(ka(),t+3*B/4,-0.4,0.7,'drum')
# taiko roll 26-30 and 40-44 accelerating, aligned with 0.5s cuts
for k in range(16): add(taiko(0.3+0.5*k/16),26+3+k*B/8*0+k*0.0625,0,1,'drum') if False else None
for k in range(16): add(taiko(0.25+0.55*k/16),28+k*B/4,0,1,'drum')
for k in range(8): add(taiko(1.0,True),40+k*B,0,1,'drum'); add(braam([38,45,50],0.6),40+k*B,0,0.25)
for k in range(16): add(taiko(0.3+0.5*k/16),42+k*B/8,0,1,'drum')
# braams & booms at section hits
for s_,g_ in [(6,1.0),(18,0.7),(30,1.0),(44,1.2)]:
    add(braam([38,45,50,53],3.0),s_,0,0.55*g_); add(boom(g_),s_,0,0.8,'drum'); whoosh(s_)
for s_ in [34,38]: add(braam([34,41,46],2.0),s_,0,0.35)
riser(0.5,5.5,0.3); riser(16,2,0.2); riser(26,4,0.3); riser(40,4,0.32)
# final choir chord
add(choir([50,57,62,65,69],6.5),44,0,0.35)
# --- reverb
def ir(d=2.6):
    t=tt(d); return np.stack([np.random.randn(len(t))*np.exp(-t*2.6) for _ in range(2)],1)*0.02
IR=ir()
def verb(x,w): return x+w*np.stack([ss.fftconvolve(x[:,c],IR[:,c])[:N] for c in range(2)],1)
mus=verb(bus['mus'],0.9); dr=verb(bus['drum'],0.35); fx=verb(bus['fx'],0.6)
x=mus+dr+fx; x/=np.percentile(np.abs(x),99.95); mix=np.tanh(1.4*x)/np.tanh(1.4)
mix=hpf(mix.T,28).T if False else mix
mix/=np.abs(mix).max()/0.9
f=int(1.5*SR); mix[-f:]*=np.linspace(1,0,f)[:,None]
with wave.open('music3.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype('<i2').tobytes())
print('ok')
