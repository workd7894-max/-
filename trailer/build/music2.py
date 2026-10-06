import numpy as np, wave
SR=44100; BPM=120; B=60/BPM; T=50.0
N=int(SR*T); L=np.zeros(N); R=np.zeros(N); ML=np.zeros(N); MR=np.zeros(N); kicks=[]
t_all=np.arange(N)/SR
def add(sig,start,pan=0.0,g=1.0,bus='d'):
    i=int(start*SR); j=min(N,i+len(sig)); s=sig[:j-i]*g
    a,b=(L,R) if bus=='d' else (ML,MR)
    a[i:j]+=s*(1-pan); b[i:j]+=s*(1+pan)
def env(n,a=0.005,d=0.2,sus=0.0,rel=0.05):
    t=np.arange(n)/SR; e=np.minimum(1,t/max(a,1e-4))*np.exp(-t/d)*(1-sus)+sus
    r=int(rel*SR); e[-r:]*=np.linspace(1,0,r); return e
def kick():
    n=int(0.45*SR); t=np.arange(n)/SR; f=45+110*np.exp(-t*30)
    ph=2*np.pi*np.cumsum(f)/SR; return np.tanh(2*np.sin(ph)*np.exp(-t*7))
def snare():
    n=int(0.3*SR); t=np.arange(n)/SR; nz=np.random.randn(n)
    return (0.6*nz*np.exp(-t*18)+0.5*np.sin(2*np.pi*190*t)*np.exp(-t*25))
def hat(o=False):
    n=int((0.18 if o else 0.05)*SR); t=np.arange(n)/SR; nz=np.random.randn(n)
    nz=np.diff(np.concatenate([[0],nz])); return nz*np.exp(-t*(15 if o else 70))*0.5
def saw(f,dur,det=(0,)):
    t=np.arange(int(dur*SR))/SR; s=0
    for d in det: s=s+ 2*((t*f*(1+d))%1)-1
    return s/len(det)
def lp(x,a): # one-pole lowpass
    y=np.zeros_like(x); p=0
    for i in range(len(x)): p+=a*(x[i]-p); y[i]=p
    return y
def lpf(x,a):
    import scipy.signal as ss; b,aa=ss.butter(2,a); return ss.lfilter(b,aa,x)
def note(m): return 440*2**((m-69)/12)
# chord prog Am F C G (minor heroic) each 2 bars = 4s? use 1 bar (2s) per chord
prog=[(57,[57,60,64]),(53,[53,57,60]),(48,[52,55,60]),(55,[55,59,62])]
def impact(start,g=1.0):
    n=int(2.5*SR); t=np.arange(n)/SR
    boom=np.sin(2*np.pi*(40+60*np.exp(-t*8))*t)*np.exp(-t*2)
    nz=lpf(np.random.randn(n),0.08)*np.exp(-t*3)
    add(np.tanh(1.5*(boom+0.8*nz)),start,0,0.9*g)
def riser(start,dur,g=0.35):
    n=int(dur*SR); t=np.arange(n)/SR; k=t/dur
    nz=np.random.randn(n); import scipy.signal as ss
    out=np.zeros(n); seg=int(0.05*SR)
    for i in range(0,n,seg):
        c=min(0.95,0.01+0.4*k[i]**2); b,a=ss.butter(2,[c*0.5,c],'bandpass')
        out[i:i+seg]=ss.lfilter(b,a,nz[i:i+seg])
    sw=np.sin(2*np.pi*np.cumsum(200+1800*k**2)/SR)*0.3
    add((out+sw)*k**1.5,start,0,g)
# pad entire track
for bar in range(25):
    st=bar*4*B; root,ch=prog[bar%4]; dur=4*B
    sec_g=0.35 if st<8 else (0.22 if st<44 else 0.35)
    pad=sum(saw(note(m),dur+0.3,(0,0.004,-0.004)) for m in ch)/3
    pad=lpf(pad,0.05 if st<8 else 0.12)*env(len(pad),a=0.3,d=99,sus=1,rel=0.3)
    if st<44 or st<48: add(pad,st,-0.2,sec_g,bus='m'); add(pad,st,0.2,sec_g*0.8,bus='m')
    # bass from 8s
    if 8<=st<44:
        for k8 in range(8):
            b=saw(note(root-12),B/2*0.9); b=lpf(b,0.06)*env(len(b),d=0.15,rel=0.02)
            add(np.tanh(2*b),st+k8*B/2,0,0.35,bus='m')
    # arp from 8s
    if 8<=st<44:
        arp=ch+[ch[1]+12,ch[2]+12,ch[0]+12,ch[2]+12,ch[1]+12]
        step=B/4 if st>=18 else B/2
        k=0; tt=st
        while tt<st+4*B-1e-6:
            m=arp[k%len(arp)]+12; s=saw(note(m),step*0.9,(0,0.006))
            s=lpf(s,0.2)*env(len(s),d=0.08,rel=0.01)
            add(s,tt,0.4 if k%2 else -0.4,0.12 if st<30 else 0.15,bus='m'); k+=1; tt+=step
    # lead melody in drop
    if 30<=st<44:
        mel=[ch[2]+12,ch[1]+12,ch[0]+12,ch[1]+12]
        for i,m in enumerate(mel):
            s=saw(note(m),B*0.95,(0,0.01,-0.01)); s=lpf(s,0.25)*env(len(s),a=0.01,d=1,sus=0.6,rel=0.05)
            add(s,st+i*B,0,0.13,bus='m')
# drums
for i in range(100):
    t=i*B
    if 8<=t<44:
        add(kick(),t,0,0.95); kicks.append(t)
        if t>=18 and i%2==1: add(snare(),t,0,0.45)
        if t>=18:
            add(hat(),t+B/2,0.3,0.6)
            if t>=30: add(hat(),t+B/4,-0.3,0.4); add(hat(),t+3*B/4,-0.3,0.4)
def crash(st,g=0.35):
    n=int(2.0*SR); tt=np.arange(n)/SR; nz=np.random.randn(n); nz=np.diff(np.concatenate([[0],nz]))
    add(nz*np.exp(-tt*2.2),st,0,g)
for c in [8,18,30,44]: crash(c,0.4)
for k in range(8): add(kick(),40+k*B/2,0,0.8); kicks.append(40+k*B/2)
for k in range(8): add(snare(),42+k*B/4,0,0.3+0.3*k/8)
# snare roll before drop 28-30
for k in range(16): add(snare(),28+k*B/4,0,0.15+0.3*k/16)
# fills / risers / impacts
riser(0.5,5.5); impact(6.0,1.0)
riser(16,2,0.25); impact(18.0,0.6)
riser(26,4,0.35); impact(30.0,1.0)
riser(40,4,0.4); impact(44.0,1.2)
# outro chord swell 44-50
ch=[57,60,64,69]
pad=sum(saw(note(m),6,(0,0.004,-0.004)) for m in ch)/4
pad=lpf(pad,0.15)*np.exp(-np.arange(len(pad))/SR/2.5)
add(pad,44,0,0.4)
sc=np.ones(N)
for k in kicks:
    i=int(k*SR); n=int(0.35*SR); j=min(N,i+n); e=1-0.75*np.exp(-np.arange(j-i)/SR/0.09); sc[i:j]=np.minimum(sc[i:j],e)
L=np.tanh(1.3*L)+ML*sc; R=np.tanh(1.3*R)+MR*sc
mix=np.stack([L,R],1); mix/=np.abs(mix).max()/0.89
fade=int(1.0*SR); mix[-fade:]*=np.linspace(1,0,fade)[:,None]
with wave.open('music2.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix*32767).astype('<i2').tobytes())
print('ok')
