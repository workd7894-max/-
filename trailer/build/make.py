import subprocess, os, sys
S=os.path.dirname(os.path.abspath(__file__)); C=S+'/../clips/'; F=S+'/../fonts/'
clip={n:C+f for f in os.listdir(C) for n in [int(f.split('.')[0])]}
# (clip, src_start, dur, title, sub, flash)
E=[
 (10, 5.0, 3.0, '여신의 축복을 받은', '', 0),
 (1, 36.5, 3.0, '영웅들이 깨어난다', '', 0),
 ('logo', 0, 2.0, '', '', 1),
 (1, 54.5, 2.0, '시그너스 영웅 소환', '화려한 컷신과 함께 등장', 1),
 (1, 69.0, 2.0, '', '', 0),
 (12, 2.0, 2.0, '수많은 유닛 수집', '', 1),
 (3, 8.0, 2.0, '수백 가지 코디 아이템', '나만의 스타일로 꾸미기', 1),
 (2, 14.0, 2.0, '코디 그대로 전투에', '실시간 반영', 0),
 (7, 30.0, 2.0, '', '', 1),
 (9, 17.0, 2.0, '화려한 전투', '', 1),
 (10, 5.3, 2.0, '여신의 가호', '광역 버프 발동', 1),
 (11, 14.2, 2.0, '', '', 0),
 (5, 36.0, 2.0, '테마 던전', '강화하고, 막아내라', 1),
 (5, 88.0, 2.0, '최종 무기, 최종 보스', '', 0),
 (13, 5.0, 2.0, '마왕 발록', 'BOSS 1', 1),
 (13, 23.0, 2.0, '', '', 0),
 (14, 36.0, 2.0, '로그라이크 버프', '', 1),
 (15, 11.0, 2.0, '파풀라투스', 'BOSS 2', 1),
 (16, 8.0, 2.0, '좌·우 피아누스', 'BOSS 3', 1),
 (16, 21.0, 1.0, '', '', 1),
 (13, 17.0, 1.0, '', '', 1),
 (15, 4.0, 1.0, '', '', 1),
 (16, 44.0, 1.0, '', '', 1),
 ('end', 0, 6.0, '', '', 1),
]
def esc(s): return s.replace(':','\\:').replace("'","\\'")
def txt(title,sub,d):
    f=[]
    if title:
        a=f"if(lt(t,0.15),t/0.15,1)"
        f.append(f"drawtext=fontfile={F}BlackHanSans-Regular.ttf:text='{esc(title)}':fontsize=104:fontcolor=white:borderw=7:bordercolor=0x1a0d00:shadowx=0:shadowy=6:shadowcolor=black@0.6:x=(w-text_w)/2:y='h-250-(1-min(t/0.2,1))*30':alpha='{a}'")
    if sub:
        f.append(f"drawtext=fontfile={F}DoHyeon-Regular.ttf:text='{esc(sub)}':fontsize=54:fontcolor=0xFFD27A:borderw=5:bordercolor=0x1a0d00:x=(w-text_w)/2:y=h-130:alpha='if(lt(t,0.25),t/0.25,1)'")
    return f
os.makedirs(S+'/seg',exist_ok=True)
lst=[]
for i,(c,ss,d,ti,su,fl) in enumerate(E):
    out=f"{S}/seg/{i:02d}.mp4"; lst.append(out)
    if c=='logo':
        vf=f"[1]scale=1100:-1,format=rgba,fade=in:st=0:d=0.4:alpha=1[l];[0][l]overlay=(W-w)/2:(H-h)/2,zoompan=z='1+0.03*on/60':d=1:s=1920x1080:fps=30"
        cmd=['ffmpeg','-v','error','-y','-f','lavfi','-i',f'color=0x0b0f17:s=1920x1080:r=30:d={d}','-loop','1','-t',str(d),'-i',S+'/logo.png','-filter_complex',vf]
    elif c=='end':
        vf=(f"[1]scale=1000:-1,format=rgba,fade=in:st=0.2:d=0.8:alpha=1[l];[0]eq=brightness=-0.25:saturation=0.6,gblur=sigma=12[bg];[bg][l]overlay=(W-w)/2:(H-h)/2-90,"
            f"drawtext=fontfile={F}BlackHanSans-Regular.ttf:text='지금 플레이하세요':fontsize=88:fontcolor=white:borderw=6:bordercolor=0x2a1400:x=(w-text_w)/2:y=h-230:alpha='if(lt(t,1.4),0,min((t-1.4)/0.5,1))',fade=out:st={d-0.8}:d=0.8")
        cmd=['ffmpeg','-v','error','-y','-ss','40','-t',str(d),'-i',clip[16],'-loop','1','-t',str(d),'-i',S+'/logo.png','-filter_complex',vf]
        cmd[cmd.index('-filter_complex')+1]=vf.replace('[0]eq','[0]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,eq')
    else:
        f=["scale=1920:1080:force_original_aspect_ratio=increase","crop=1920:1080","fps=30","setsar=1"]
        if i<2: f.append("eq=brightness=-0.08:saturation=0.85")
        if i==0: f.append("fade=in:st=0:d=0.8")
        if fl: f.append("fade=in:st=0:d=0.12:color=white")
        f+=txt(ti,su,d)
        cmd=['ffmpeg','-v','error','-y','-ss',str(ss),'-t',str(d),'-i',clip[c],'-vf',','.join(f)]
    cmd+=['-an','-t',str(d),'-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-r','30',out]
    subprocess.run(cmd,check=True)
with open(S+'/seg/list.txt','w') as fh:
    for p in lst: fh.write(f"file '{p}'\n")
tot=sum(e[2] for e in E); print('total',tot)
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',S+'/seg/list.txt','-i',S+'/music.wav','-map','0:v','-map','1:a','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',S+'/trailer.mp4'],check=True)
