import subprocess, os, sys
S=os.path.dirname(os.path.abspath(__file__)); C=S+'/../clips/'; F=S+'/../fonts/'
clip={int(f.split('.')[0]):C+f for f in os.listdir(C)}
BH=F+'BlackHanSans-Regular.ttf'
def esc(s): return s.replace(':','\\:').replace("'","\\'").replace(',','\\,')
# entries: ('c', clip, src, dur, opts) | ('card', dur, text, bg(clip,src)|None) | ('black',dur) | ('logo',dur,end?)
E=[
 ('i',0.0,2.5),
 ('c',1,55.0,0.5,dict(z=1.05,hit=1)),
 ('i',3.0,2.5),
 ('c',1,69.6,0.5,dict(z=1.05,hit=1)),
 ('i',6.0,2.0),
 ('c',13,6.0,0.5,dict(hit=1)),
 ('i',8.5,3.5),
 ('logo',2.0,0),
 ('card',1.0,'영웅을 소환하라',(1,56.0)),
 ('c',1,69.3,2.0,dict(z=1.05,push=1)),
 ('c',1,57.2,1.0,dict(z=1.1)),
 ('c',12,2.0,1.5,dict(z=1.12,lab=('COLLECT','수많은 유닛'))),
 ('c',3,8.0,1.5,dict(z=1.15,lab=('CUSTOMIZE','수백 가지 코디'))),
 ('c',2,14.0,1.5,dict(lab=('REAL-TIME','코디 그대로 전투에'))),
 ('c',8,10.0,1.5,dict(z=1.12,lab=('ACHIEVEMENT','다양한 업적 보상'))),
 ('c',7,30.0,2.0,dict(push=1)),
 ('card',1.0,'전장을 지배하라',(9,30.0)),
 ('c',9,17.0,1.0,dict(hit=1)),
 ('c',6,30.0,1.0,dict()),
 ('c',10,5.3,2.0,dict(z=1.15,lab=('BLESSING','여신의 가호'))),
 ('c',11,14.2,1.5,dict(hit=1)),
 ('c',4,10.0,2.0,dict(lab=('THEME DUNGEON','강화하고 막아내라'))),
 ('c',5,36.0,2.0,dict(push=1)),
 ('c',5,88.0,1.5,dict(hit=1,sp=1.3)),
 ('c',9,54.0,1.5,dict(hit=1)),
 ('black',0.5),
 ('c',13,5.0,2.0,dict(hit=1,flash=1,ramp=1,lab=('BOSS 01','마왕 발록'))),
 ('c',13,23.0,1.0,dict(hit=1)),
 ('c',14,36.0,1.0,dict(z=1.1,lab=('ROGUELIKE','스테이지마다 새로운 버프'))),
 ('c',14,93.0,1.0,dict(hit=1)),
 ('c',14,75.0,1.0,dict(hit=1)),
 ('c',15,11.0,2.0,dict(hit=1,ramp=1,lab=('BOSS 02','파풀라투스'))),
 ('c',15,0.5,1.0,dict(hit=1)),
 ('c',16,8.0,2.0,dict(hit=1,lab=('BOSS 03','피아누스'))),
 ('c',16,27.0,1.0,dict(hit=1)),
]+[('c',c,s,0.5,dict(hit=1,z=1.3)) for c,s in [(16,21.0),(13,17.0),(15,4.0),(16,44.0),(9,30.0),(13,36.0),(15,13.0)]]+[
 ('black',0.5),
 ('logo',6.0,1),
]
GR="eq=contrast=1.12:saturation=1.25:gamma=0.97,vignette=PI/4.2,noise=alls=6:allf=t"
BARS="drawbox=x=0:y=0:w=iw:h=100:color=black:t=fill,drawbox=x=0:y=ih-100:w=iw:h=100:color=black:t=fill"
ENC=['-an','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-r','30']
def frame(z,push,d,cy=0.47):
    # crop into the action (hide HUD), slow push-in
    zz=f"{z}+{0.07 if push else 0.025}*t/{d}"
    return [f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1",
            f"scale='ceil(1920*({zz})/2)*2':-2:eval=frame",
            f"crop=1920:1080:x='(iw-1920)/2':y='(ih-1080)*{cy}'"]
def label(en,kr):
    sp=' '.join(en)
    return [f"drawbox=x=110:y=ih-262:w='min(t/0.25,1)*70':h=3:color=0xF2B035:t=fill",
            f"drawtext=fontfile={BH}:text='{esc(sp)}':fontsize=28:fontcolor=0xF2B035:x=110:y=h-245:alpha='min(max(t-0.05,0)/0.2,1)'",
            f"drawtext=fontfile={BH}:text='{esc(kr)}':fontsize=70:fontcolor=white:shadowx=0:shadowy=4:shadowcolor=black@0.8:x='110-25*max(0,1-t/0.3)':y=h-205:alpha='min(max(t-0.1,0)/0.25,1)'"]
def card_text(txt,d):
    return [f"drawbox=x='(iw-min(t/0.35,1)*620)/2':y=ih/2-100:w='min(t/0.35,1)*620':h=2:color=0xF2B035@0.9:t=fill",
            f"drawbox=x='(iw-min(t/0.35,1)*620)/2':y=ih/2+98:w='min(t/0.35,1)*620':h=2:color=0xF2B035@0.9:t=fill",
            f"drawtext=fontfile={BH}:text='{esc(txt)}':fontsize=110:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:alpha='min(t/0.3,1)*if(gt(t,{d}-0.15),({d}-t)/0.15,1)'"]
os.makedirs(S+'/seg4',exist_ok=True); lst=[]
for i,e in enumerate(E):
    out=f"{S}/seg4/{i:02d}.mp4"; lst.append(out); k=e[0]
    if k=='i':
        cmd=['ffmpeg','-v','error','-y','-ss',str(e[1]),'-t',str(e[2]),'-i',S+'/intro.mp4','-vf','setpts=PTS-STARTPTS','-t',str(e[2])]
    elif k=='black':
        cmd=['ffmpeg','-v','error','-y','-f','lavfi','-i',f'color=black:s=1920x1080:r=30:d={e[1]}','-t',str(e[1])]
    elif k=='card':
        d,txt,bg=e[1],e[2],e[3]
        if bg:
            vf=','.join(frame(1.1,1,d)+["gblur=sigma=14","eq=brightness=-0.32:saturation=0.6",GR,BARS]+card_text(txt,d))
            cmd=['ffmpeg','-v','error','-y','-ss',str(bg[1]),'-t',str(d+0.1),'-i',clip[bg[0]],'-vf',vf,'-t',str(d)]
        else:
            vf=','.join(["noise=alls=5:allf=t"]+card_text(txt,d))
            cmd=['ffmpeg','-v','error','-y','-f','lavfi','-i',f'color=0x050608:s=1920x1080:r=30:d={d}','-vf',vf,'-t',str(d)]
    elif k=='logo':
        d,end=e[1],e[2]
        sweep=f"[lg][sh]overlay=x='-600+(W+600)*min(t/{0.9 if not end else 1.4},1)':y=0:shortest=1,format=rgba[lgs]"
        pre=(f"[1]scale=1100:-1,format=rgba,split[a][m];[m]alphaextract[am];"
             f"color=white@0:s=1100x700,format=rgba[c0];")
        # logo settle + glow
        vf=(f"[1]scale='1100*(1.18-0.18*min(t/0.35,1)^0.5)':-1:eval=frame,format=rgba,fade=in:st=0:d=0.25:alpha=1[l];"
            f"[l]split[l1][l2];[l2]gblur=sigma=25,colorchannelmixer=aa=0.7[gl];"
            f"[0][gl]overlay=(W-w)/2:(H-h)/2-{60 if end else 0}[g];[g][l1]overlay=(W-w)/2:(H-h)/2-{60 if end else 0},"
            + ("fade=in:st=0:d=0.25:color=white," if not end else "fade=in:st=0:d=0.35:color=white,")
            + "rgbashift=rh=10:bh=-10:enable='lt(t,0.12)',"
            + f"noise=alls=5:allf=t,{BARS}" + (f",fade=out:st={d-1.3}:d=1.3" if end else ""))
        if end:
            bgv=f"[0]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,gblur=sigma=20,eq=brightness=-0.35:saturation=0.5[b];"
            vf=bgv+vf.replace("[0][gl]","[b][gl]")
            cmd=['ffmpeg','-v','error','-y','-ss','40','-t',str(d),'-i',clip[16],'-loop','1','-framerate','30','-t',str(d),'-i',S+'/logo.png','-filter_complex',vf,'-t',str(d)]
        else:
            cmd=['ffmpeg','-v','error','-y','-f','lavfi','-i',f'color=0x050608:s=1920x1080:r=30:d={d}','-loop','1','-framerate','30','-t',str(d),'-i',S+'/logo.png','-filter_complex',vf,'-t',str(d)]
    else:
        _,c,ss,d,o=e; z=o.get('z',1.22); sp=o.get('sp',1.0)
        f=[]
        if o.get('ramp'):
            # first 55% fast (1.7x), rest slow (0.55x) with frame blending
            src=d*0.55*1.7+d*0.45*0.55
            a=d*0.55*1.7
            f.append(f"setpts='if(lt(T,{a}),(PTS-STARTPTS)/1.7,({a}/1.7+(T-{a})/0.55)/TB)'")
            f.append("framerate=fps=30")
        elif sp!=1:
            src=d*sp; f.append(f"setpts=(PTS-STARTPTS)/{sp}")
        else: src=d; f.append("setpts=PTS-STARTPTS")
        f.append("fps=30")
        f+=frame(z,o.get('push'),d)
        if o.get('hit'):
            # punch-in zoom blur on cut + chroma split
            f+=["tmix=frames=3:weights='1 1 1':enable='lt(t,0.1)'","rgbashift=rh=12:bh=-12:enable='lt(t,0.1)'"]
        f.append(GR)
        if o.get('flash'): f.append("fade=in:st=0:d=0.18:color=white")
        f.append(BARS)
        if 'lab' in o: f+=label(*o['lab'])
        cmd=['ffmpeg','-v','error','-y','-ss',str(ss),'-t',str(src+0.2),'-i',clip[c],'-vf',','.join(f),'-t',str(d)]
    subprocess.run(cmd+ENC+[out],check=True)
open(S+'/seg4/list.txt','w').write(''.join(f"file '{p}'\n" for p in lst))
tot=sum(e[3] if e[0]=='c' else (e[2] if e[0]=='i' else e[1]) for e in E); print('total',tot)
