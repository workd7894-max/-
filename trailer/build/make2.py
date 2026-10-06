import subprocess, os
S=os.path.dirname(os.path.abspath(__file__)); C=S+'/../clips/'; F=S+'/../fonts/'
clip={int(f.split('.')[0]):C+f for f in os.listdir(C)}
# clip, src, dur, KR title, EN tag, flash, punch-zoom, shake, speed
E=[
 (10,5.0,3.0,'여신의 축복을 받은','',0,0,0,0.8),
 (1,54.6,3.0,'영웅들이 깨어난다','',0,0,0,1.0),
 ('logo',0,2.0,'','',1,0,1,1),
 (1,69.3,2.0,'시그너스 영웅 소환','SUMMON',1,1,0,1),
 (1,57.2,1.0,'','',1,1,0,1),
 (12,2.0,1.5,'수많은 유닛 수집','COLLECT',1,1,0,1),
 (3,8.0,2.0,'수백 가지 코디','CUSTOMIZE',1,1,0,1),
 (2,14.0,1.5,'코디 그대로 전투에','REAL-TIME',1,1,0,1),
 (7,30.0,2.0,'','',1,1,1,1),
 (6,30.0,1.0,'','',1,1,1,1),
 (9,17.0,1.0,'화려한 전투','BATTLE',1,1,1,1),
 (10,5.3,2.0,'여신의 가호','BLESSING',1,1,1,1),
 (11,14.2,2.0,'','',1,1,1,1),
 (4,10.0,2.0,'강화하고, 막아내라','THEME DUNGEON',1,1,0,1),
 (5,36.0,2.0,'','',1,1,1,1),
 (5,88.0,1.0,'','',1,1,1,1.3),
 (9,54.0,1.0,'','',1,1,1,1),
 (13,5.0,2.0,'마왕 발록','BOSS 01',1,1,1,1),
 (13,23.0,1.0,'','',1,1,1,1),
 (14,36.0,1.0,'로그라이크 버프','ROGUELIKE',1,1,0,1),
 (14,93.0,1.0,'','',1,1,1,1),
 (15,11.0,2.0,'파풀라투스','BOSS 02',1,1,1,1),
 (16,8.0,2.0,'피아누스','BOSS 03',1,1,1,1),
 (16,27.0,1.0,'','',1,1,1,1),
 (16,21.0,0.5,'','',1,1,1,1),(13,17.0,0.5,'','',1,1,1,1),
 (15,4.0,0.5,'','',1,1,1,1),(16,44.0,0.5,'','',1,1,1,1),
 (9,30.0,0.5,'','',1,1,1,1),(13,36.0,0.5,'','',1,1,1,1),
 (15,13.0,0.5,'','',1,1,1,1),(16,45.0,0.5,'','',1,1,1,1),
 ('end',0,6.0,'','',1,0,0,1),
]
def esc(s): return s.replace(':','\\:').replace("'","\\'").replace(',','\\,')
GRADE="eq=contrast=1.15:saturation=1.3:gamma=0.95,vignette=PI/4.5,unsharp=5:5:0.6"
BARS="drawbox=x=0:y=0:w=iw:h=96:color=black:t=fill,drawbox=x=0:y=ih-96:w=iw:h=96:color=black:t=fill"
def text(kr,en):
    f=[]
    if en:
        f.append(f"drawbox=x='120-300*max(0,1-t/0.2)':y=ih-330:w=8:h=150:color=0xF2B035@0.95:t=fill")
        f.append(f"drawtext=fontfile={F}BlackHanSans-Regular.ttf:text='{esc(en)}':fontsize=40:fontcolor=0xF2B035:x='150-200*max(0,1-t/0.2)':y=h-330:alpha='min(t/0.15,1)'")
    if kr:
        x="150-260*max(0,1-t/0.22)" if en else "(w-text_w)/2"
        y="h-285" if en else "h-300"
        f.append(f"drawtext=fontfile={F}BlackHanSans-Regular.ttf:text='{esc(kr)}':fontsize={96 if en else 92}:fontcolor=white:borderw=3:bordercolor=black@0.7:shadowx=0:shadowy=8:shadowcolor=black@0.7:x='{x}':y={y}:alpha='min(t/0.15,1)'")
    return f
os.makedirs(S+'/seg2',exist_ok=True); lst=[]
for i,(c,ss,d,kr,en,fl,pz,sk,sp) in enumerate(E):
    out=f"{S}/seg2/{i:02d}.mp4"; lst.append(out)
    if c=='logo':
        vf=(f"[1]scale='1150*(1.25-0.25*min(t/0.25,1))':-1:eval=frame,format=rgba,fade=in:st=0:d=0.15:alpha=1[l];"
            f"[0][l]overlay=(W-w)/2:(H-h)/2,fade=in:st=0:d=0.2:color=white,crop=1920:1080:x='10*sin(t*80)*exp(-t*6)':y='8*cos(t*70)*exp(-t*6)',pad=1940:1100:10:10,scale=1920:1080,{BARS}")
        cmd=['ffmpeg','-v','error','-y','-f','lavfi','-i',f'color=0x07090d:s=1920x1080:r=30:d={d}','-loop','1','-framerate','30','-t',str(d),'-i',S+'/logo.png','-filter_complex',vf]
    elif c=='end':
        vf=(f"[0]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,eq=brightness=-0.3:saturation=0.5,gblur=sigma=18[bg];"
            f"[1]scale='1050*(1.15-0.15*min(t/0.6,1))':-1:eval=frame,format=rgba,fade=in:st=0:d=0.5:alpha=1[l];"
            f"[bg][l]overlay=(W-w)/2:(H-h)/2,fade=in:st=0:d=0.3:color=white,{BARS},fade=out:st={d-1.2}:d=1.2")
        cmd=['ffmpeg','-v','error','-y','-ss','40','-t',str(d),'-i',clip[16],'-loop','1','-framerate','30','-t',str(d),'-i',S+'/logo.png','-filter_complex',vf]
    else:
        f=[f"setpts=PTS/{sp}" if sp!=1 else "null","scale=1920:1080:force_original_aspect_ratio=increase","crop=1920:1080","fps=30","setsar=1"]
        if pz: f.append("scale='2112*(1-0.06*min(t/0.25,1))':-2:eval=frame,crop=1920:1080")
        else: f.append("scale='1920*(1+0.04*t/3)':-2:eval=frame,crop=1920:1080")
        if sk: f.append("pad=1960:1120:20:20,crop=1920:1080:x='20+14*sin(t*95)*exp(-t*7)':y='20+10*cos(t*83)*exp(-t*7)'")
        f.append(GRADE)
        if i==0: f.append("fade=in:st=0:d=1.0")
        if fl: f.append("fade=in:st=0:d=0.1:color=white")
        f.append(BARS); f+=text(kr,en)
        cmd=['ffmpeg','-v','error','-y','-ss',str(ss),'-t',str(d*sp+0.1),'-i',clip[c],'-vf',','.join(f)]
    cmd+=['-an','-t',str(d),'-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-r','30',out]
    subprocess.run(cmd,check=True)
open(S+'/seg2/list.txt','w').write(''.join(f"file '{p}'\n" for p in lst))
print('total',sum(e[2] for e in E))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',S+'/seg2/list.txt','-i',S+'/music2.wav','-map','0:v','-map','1:a','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',S+'/trailer2.mp4'],check=True)
