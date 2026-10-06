# custom 6s intro animation: gold dust, falling maple leaves, light converging into a sword beam
import numpy as np, subprocess, math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont
S=os.path.dirname(os.path.abspath(__file__)); F=S+'/../fonts/BlackHanSans-Regular.ttf'
W,H,FPS,D=1920,1080,30,12.0; NF=int(FPS*D)
rng=np.random.default_rng(5)
# background: radial gradient + soft fog texture
yy,xx=np.mgrid[0:H,0:W]; r=np.hypot((xx-W/2)/W,(yy-H/2)/H)
base=np.stack([np.clip(0.06-0.07*r,0,1)*255*np.array(c) for c in [0.35,0.45,0.9]],2)
fog=np.asarray(Image.fromarray((rng.random((60,107))*255).astype('uint8')).resize((W*2,H),Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))).astype(float)/255
# particles
NP=900
px=rng.random(NP)*W; py=rng.random(NP)*H; pv=rng.random(NP)*25+8; ps=rng.random(NP)**3*3+0.8; pph=rng.random(NP)*6.28
# leaves
def leaf_poly(cx,cy,s,a,flip=1.0):
    pts=[]
    for k in range(160):
        th=k/160*2*math.pi
        r=0.30+0.70*abs(math.cos(2.5*th))**2.5+0.10*abs(math.cos(17.5*th))**6
        if abs(th-math.pi)<0.22: r=0.12
        ang=th-math.pi/2; x=s*r*math.cos(ang)*flip; y=s*r*math.sin(ang)
        ca,sa=math.cos(a),math.sin(a)
        pts.append((cx+x*ca-y*sa,cy+x*sa+y*ca))
    return pts
NL=26
lx=rng.random(NL)*W; ly=-rng.random(NL)*H*0.8-60; lvs=rng.random(NL)*90+70; lsz=rng.random(NL)*26+22; lrot=rng.random(NL)*6; lsp=(rng.random(NL)-.5)*3
font_cache={}
def font(sz):
    if sz not in font_cache: font_cache[sz]=ImageFont.truetype(F,sz)
    return font_cache[sz]
def text_layer(txt,a,blur,scale=1.0):
    L=Image.new('L',(W,H),0); d=ImageDraw.Draw(L); f=font(int(104*scale))
    bb=d.textbbox((0,0),txt,font=f); d.text(((W-(bb[2]-bb[0]))/2,(H-(bb[3]-bb[1]))/2-20),txt,font=f,fill=int(255*a))
    if blur>0.3: L=L.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(L).astype(float)/255
def ease(x): x=min(max(x,0),1); return x*x*(3-2*x)
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','16','-preset','medium','-pix_fmt','yuv420p',S+'/intro.mp4'],stdin=subprocess.PIPE)
for n in range(NF):
    t=n/FPS
    img=base.copy()
    fo=fog[:, int(t*40)%W:int(t*40)%W+W]
    img+=fo[:,:,None]*np.array([30,24,12])*(0.5+0.5*ease(t/3))
    # converge factor 3.8 -> 5.8
    cv=ease((t-8.6)/3.0)
    tx=px+np.sin(pph+t*1.3)*12; ty=(py-pv*t)%H
    tx=tx+(W/2-tx)*cv**1.5; ty=ty+(H/2-ty)*cv**2*0.3
    lay=Image.new('L',(W,H),0); d=ImageDraw.Draw(lay)
    tw=0.55+0.45*np.sin(pph*3+t*4)
    for i in range(NP):
        s=ps[i]*(1+cv*0.8); a=int(255*tw[i]*min(1,0.25+t/1.2))
        d.ellipse((tx[i]-s,ty[i]-s,tx[i]+s,ty[i]+s),fill=a)
    pa=np.asarray(lay).astype(float)/255
    glow=np.asarray(lay.filter(ImageFilter.GaussianBlur(6))).astype(float)/255
    gold=np.array([255,196,110])
    img+= (pa[:,:,None]*gold*0.9 + glow[:,:,None]*gold*1.6)
    # leaves (fall from t=1.2)
    if t>2.3:
        ll=Image.new('RGBA',(W,H),(0,0,0,0)); dl=ImageDraw.Draw(ll)
        for i in range(NL):
            tt_=t-2.3; cx=lx[i]+math.sin(tt_*1.5+i)*60; cy=ly[i]+lvs[i]*tt_*1.6
            cx=cx+(W/2-cx)*cv; cy=cy+(H/2-cy)*cv*0.6
            if cy<-80 or cy>H+80: continue
            sz=lsz[i]*(1-0.7*cv); rot=lrot[i]+lsp[i]*tt_
            col=(235,int(90+40*(i%3)/2),40,int(230*(1-cv)))
            dl.polygon(leaf_poly(cx,cy,sz,rot,0.35+0.65*abs(math.cos(tt_*2+i))),fill=col)
        lb=ll.filter(ImageFilter.GaussianBlur(1.2)); la=np.asarray(lb).astype(float)
        a=la[:,:,3:4]/255; img=img*(1-a)+la[:,:,:3]*a
        lg=np.asarray(ll.filter(ImageFilter.GaussianBlur(14))).astype(float)
        img+=lg[:,:,:3]*(lg[:,:,3:4]/255)*0.5
    # vertical light beam / sword (4.2 -> 6)
    bm=ease((t-9.4)/2.6)
    if bm>0:
        g=H/2-140; tip=g+560*bm; top=g-170*bm
        m=Image.new('L',(W,H),0); dm=ImageDraw.Draw(m); cx=W/2
        bw=30
        dm.polygon([(cx-bw,g),(cx+bw,g),(cx+bw*0.8,g+(tip-g)*0.85),(cx,tip),(cx-bw*0.8,g+(tip-g)*0.85)],fill=255)
        dm.rectangle((cx-9,top,cx+9,g),fill=230)
        dm.ellipse((cx-18,top-30,cx+18,top+6),fill=255)
        gw=170*bm
        dm.polygon([(cx-gw,g-6),(cx,g-22),(cx+gw,g-6),(cx+gw-20,g+10),(cx,g+4),(cx-gw+20,g+10)],fill=255)
        mk=np.asarray(m.filter(ImageFilter.GaussianBlur(1.5))).astype(float)/255
        g1=np.asarray(m.filter(ImageFilter.GaussianBlur(12))).astype(float)/255
        g2=np.asarray(m.filter(ImageFilter.GaussianBlur(45))).astype(float)/255
        halo=np.exp(-((xx-W/2)**2+(yy-H/2)**2)/(2*(150+220*bm)**2))*bm
        img+=mk[:,:,None]*np.array([255,248,225])*1.4*bm+g1[:,:,None]*np.array([255,210,140])*1.3*bm+g2[:,:,None]*np.array([255,160,70])*1.6*bm+halo[:,:,None]*np.array([255,150,60])*0.35
    # text
    for (txt,t0,t1) in [('여신이 선택한',0.3,2.2),('영웅들이 깨어난다',3.2,5.2),('전설이 시작된다',6.2,7.8)]:
        if t0<=t<=t1+0.3:
            k=ease((t-t0)/0.6); out=ease((t-t1)/0.3)
            tl=text_layer(txt,k*(1-out),(1-k)*14+out*10,1.0+0.04*(t-t0))
            img=img*(1-tl[:,:,None]*0.9)+tl[:,:,None]*np.array([250,244,230])
            tg=np.asarray(Image.fromarray((tl*255).astype('uint8')).filter(ImageFilter.GaussianBlur(18))).astype(float)/255
            img+=tg[:,:,None]*np.array([255,180,90])*0.5
    # letterbox
    img[:100]=0; img[-100:]=0
    fr=np.clip(img,0,255).astype('uint8')
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait(); print('intro done')
