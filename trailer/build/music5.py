import numpy as np, wave, scipy.signal as ss
np.random.seed(3)
SR=44100; B=0.5; T=62.0; N=int(SR*T)
bus={k:np.zeros((N,2)) for k in ['drum','mus','fx','bass']}
kicks=[]
def add(sig,st,pan=0.0,g=1.0,b='mus'):
    i=int(st*SR)
    if i>=N or i<0: return
    if sig.ndim==1: sig=np.stack([sig*(1-pan),sig*(1+pan)],1)
    j=min(N,i+len(sig)); bus[b][i:j]+=sig[:j-i]*g
def lpf(x,fc,o=2): b,a=ss.butter(o,min(fc/(SR/2),0.99)); return ss.lfilter(b,a,x,axis=0)
def hpf(x,fc,o=2): b,a=ss.butter(o,fc/(SR/2),'high'); return ss.lfilter(b,a,x,axis=0)
def bpf(x,lo,hi): b,a=ss.butter(2,[lo/(SR/2),min(hi/(SR/2),0.99)],'band'); return ss.lfilter(b,a,x,axis=0)
def sweep_lpf(x,f0,f1,seg=0.02):
    n=len(x); out=np.zeros_like(x); s=int(seg*SR); zi=None
    for i in range(0,n,s):
        k=i/n; fc=f0*(f1/f0)**k; b,a=ss.butter(2,min(fc/(SR/2),0.99))
        out[i:i+s]=ss.lfilter(b,a,x[i:i+s],axis=0)
    return out
def tt(d): return np.arange(int(d*SR))/SR
def nf(m): return 440*2**((m-69)/12)
def env(n,a,r):
    e=np.ones(n); A=min(int(a*SR),n//2); R=min(int(r*SR),n//2)
    if A: e[:A]=np.linspace(0,1,A)
    if R: e[-R:]*=np.linspace(1,0,R)
    return e
def envc(*a): return env(*a)[:,None]
def osc_saw(f,t,ph): return 2*((f*t+ph)%1)-1
def supersaw(notes,d,v=7,sp=0.018):
    t=tt(d); L=0; R=0
    for m in notes:
        for k in range(v):
            det=1+sp*(k-(v-1)/2)/((v-1)/2); s=osc_saw(nf(m)*det,t,np.random.rand())
            pan=(k-(v-1)/2)/((v-1)/2)
            L=L+s*(1-0.8*pan); R=R+s*(1+0.8*pan)
    out=np.stack([L,R],1)/(len(notes)*v)*2.2
    return hpf(out,150)
def kick():
    t=tt(0.5); f=48+180*np.exp(-t*35)
    body=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*6)
    click=hpf(np.random.randn(len(t)),3000)*np.exp(-t*300)*0.5
    return np.tanh(2.5*(body+click))
def clap():
    t=tt(0.6); nz=bpf(np.random.randn(len(t)),900,6000); e=np.zeros(len(t))
    for o in [0,0.011,0.022]: i=int(o*SR); e[i:]+=np.exp(-(t[:len(t)-i])*60)
    e+=0.5*np.exp(-t*9); return nz*e*0.8
def hat(op=False):
    t=tt(0.25 if op else 0.06); return hpf(np.random.randn(len(t)),7000)*np.exp(-t*(12 if op else 80))*0.5
def snare():
    t=tt(0.2); return (bpf(np.random.randn(len(t)),1500,8000)*np.exp(-t*25)+0.5*np.sin(2*np.pi*200*t)*np.exp(-t*30))
def reese(m,d,wob=0):
    t=tt(d); f=nf(m)
    x=osc_saw(f*0.995,t,0)+osc_saw(f*1.005,t,0.3)+0.6*osc_saw(f*2.003,t,.6)
    sub=np.sin(2*np.pi*f*t)
    if wob:
        lfo=0.5-0.5*np.cos(2*np.pi*wob*t)
        out=np.zeros_like(x); s=int(0.01*SR)
        for i in range(0,len(x),s):
            fc=150+2600*lfo[i]; b,a=ss.butter(2,fc/(SR/2)); out[i:i+s]=ss.lfilter(b,a,x[i:i+s])
        x=out
    else: x=lpf(x,700)
    return np.tanh(1.8*(0.6*x+0.9*sub))*env(len(t),0.005,0.03)
def pluck(m,d):
    t=tt(d); x=supersaw([m],d,5,0.01)
    return lpf(x,4000)*np.exp(-t*7)[:,None]
def impact(st,g=1.0):
    t=tt(3); f=32+90*np.exp(-t*5); boom=np.tanh(2*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*1.2))
    add(boom,st,0,0.9*g,'drum')
    t2=tt(2.5); cr=hpf(np.random.randn(len(t2)),5000)*np.exp(-t2*1.8)*0.5; add(cr,st,0,0.6*g,'fx')
def riser(st,d,g=0.35):
    x=np.random.randn(int(d*SR)); y=sweep_lpf(hpf(x,200),300,14000); k=np.linspace(0,1,len(y))**2
    t=tt(d); tone=np.sin(2*np.pi*np.cumsum(200*(8**(t/d)))/SR)*0.25
    add((y+tone)*k,st,0,g,'fx')
def downlifter(st,g=0.3):
    t=tt(2); x=sweep_lpf(np.random.randn(len(t)),12000,300); add(x*np.exp(-t*1.5),st,0,g,'fx')
# progression: Dm  Bb  F  C  (2s each)
P=[(38,[62,65,69,74]),(34,[58,62,65,70]),(41,[57,60,65,69]),(36,[55,60,64,67])]
V0,BT,DR,FS,EN=14,26,40,52,56
# INTRO 0-12: dark evolving pad, sub drone, heartbeat, stingers on glimpses
for bar in range(6):
    st=bar*2; r,ch=P[bar%4]
    x=supersaw([c-12 for c in ch],2.3); add(sweep_lpf(x,200+bar*150,350+bar*300)*envc(len(x),0.4,0.4),st,0,0.5)
add(np.sin(2*np.pi*nf(26)*tt(12))*env(int(12*SR),3,0.3),0,0,0.3,'bass')
for k in range(0,24):
    tk=k*B
    if tk<8.5 and k%2==0: add(kick()*np.linspace(1,0.4,int(0.5*SR)),tk,0,0.35,'drum')
for g in [2.5,5.5,8.0]:
    impact(g,0.45); whoosh_t=tt(0.5); add(bpf(np.random.randn(len(whoosh_t)),800,6000)*np.sin(np.pi*whoosh_t/0.5),g-0.45,0,0.25,'fx')
riser(8.5,3.5,0.45)
for k in range(12): add(snare(),10+k*B/4*0+k*0.1667 if False else 10+k*(2/12),0,0.15+0.35*k/12,'drum')
impact(12.0,1.2)
x=supersaw(P[0][1],2.5); add(lpf(x,2500)*np.exp(-tt(2.5)*1.5)[:,None],12.0,0,0.6)
downlifter(12.0)
# VERSE V0..BT, BATTLE BT..DR
for bar in range(V0//2,DR//2):
    st=bar*2; r,ch=P[bar%4]
    cut=900 if st<BT else 1800+(st-BT)*250
    for k in range(4):
        s_=supersaw(ch,0.22); add(lpf(s_,cut)*envc(len(s_),0.003,0.08),st+k*B+B/2,0,0.45)
    for k in range(8):
        if st>=DR-2 and k>=7: continue
        add(reese(r,B/2*0.92),st+k*B/2,0,0.5,'bass')
    if st>=BT:
        arp=[ch[0],ch[2],ch[1]+12,ch[2],ch[3],ch[2],ch[1]+12,ch[2]]
        for k,m in enumerate(arp*2): add(pluck(m+12,B/4),st+k*B/4,0.4 if k%2 else -0.4,0.22)
for i in range(int(V0/B),int(DR/B)):
    t=i*B
    if t>=DR-0.5: break
    add(kick(),t,0,0.95,'drum'); kicks.append(t)
    add(hat(),t+B/2,0.3,0.7,'drum')
    if t>=BT:
        if i%2==1: add(clap(),t,0,0.6,'drum')
        add(hat(),t+B/4,-0.3,0.4,'drum'); add(hat(),t+3*B/4,-0.3,0.4,'drum')
impact(V0,0.5); riser(BT-2,2,0.25); impact(BT,0.6)
for k in range(8): add(snare(),DR-4+k*0.25,0,0.25+0.2*k/8,'drum')
for k in range(12): add(snare(),DR-2+k*0.125,0,0.4+0.3*k/12,'drum')
riser(DR-4,3.5,0.45)
# DROP DR..FS..EN
lead=[74,72,69,72, 70,69,65,67, 69,72,74,77, 76,74,72,67]
for bar in range(DR//2,EN//2):
    st=bar*2; r,ch=P[bar%4]
    s_=supersaw(ch,2.0); add(lpf(s_,6000)*envc(len(s_),0.005,0.05),st,0,0.42)
    s_=supersaw([c-12 for c in ch[:3]],2.0); add(lpf(s_,3000),st,0,0.2)
    add(reese(r,2.0,wob=4 if st<FS else 8),st,0,0.6,'bass')
    for k in range(4):
        m=lead[(bar*4+k)%16]; s_=supersaw([m,m+12],B*0.9,7,0.012); add(lpf(s_,7000)*envc(len(s_),0.005,0.05),st+k*B,0,0.28)
for i in range(int(DR/B),int(EN/B)):
    t=i*B
    if t>=EN-0.5: break
    add(kick(),t,0,1.0,'drum'); kicks.append(t)
    add(hat(True),t+B/2,0.2,0.5,'drum')
    add(hat(),t+B/4,-0.3,0.4,'drum'); add(hat(),t+3*B/4,0.3,0.4,'drum')
    if i%2==1: add(clap(),t,0,0.7,'drum')
for k in range(14): add(snare(),FS+k*0.25,0,0.25+0.35*k/14,'drum')
for k in range(12): add(snare(),EN-2+k*0.125,0,0.35+0.35*k/12,'drum')
riser(FS,3.5,0.4)
impact(DR,1.2); impact(DR+4,0.5); impact(DR+8,0.5)
# FINAL
impact(EN,1.4)
s_=supersaw([50,57,62,65,69,74],6.0); add(lpf(s_,5000)*np.exp(-tt(6)*0.35)[:,None],EN,0,0.8)
add(np.sin(2*np.pi*nf(26)*tt(4))*np.exp(-tt(4)*0.8),EN,0,0.5,'bass')
downlifter(EN+0.2,0.35)
# sidechain
sc=np.ones(N)
for k in kicks:
    i=int(k*SR); n=int(0.4*SR); j=min(N,i+n); sc[i:j]=np.minimum(sc[i:j],1-0.8*np.exp(-np.arange(j-i)/SR/0.11))
def ir(d=2.2):
    t=tt(d); return np.stack([np.random.randn(len(t))*np.exp(-t*3) for _ in range(2)],1)*0.02
IR=ir()
def verb(x,w): return x+w*np.stack([ss.fftconvolve(x[:,c],IR[:,c])[:N] for c in range(2)],1)
mus=verb(bus['mus'],0.6)*sc[:,None]; bass=bus['bass']*sc[:,None]
drum=bus['drum']+0.25*verb(bus['drum'],0.4)-0.25*bus['drum']; fx=verb(bus['fx'],0.5)
x=mus+bass+drum+fx; x/=np.percentile(np.abs(x),99.95); mix=np.tanh(1.5*x)/np.tanh(1.5)
mix/=np.abs(mix).max()/0.9
f=int(1.5*SR); mix[-f:]*=np.linspace(1,0,f)[:,None]
with wave.open('music5.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype('<i2').tobytes())
print([round(20*np.log10(np.sqrt((mix[s*SR:(s+2)*SR]**2).mean())+1e-9),1) for s in range(0,62,2)])
