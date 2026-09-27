"""Add captions outside preserved Electron screenshots; never draw UI rows."""
from pathlib import Path
import hashlib,json
from collections import Counter
from PIL import Image,ImageDraw,ImageFont,ImageSequence
ROOT=Path(__file__).resolve().parent
RAW=ROOT/'raw'
BG='#101218'
TEXT='#f4f4f5'
MUTED='#bbc1cc'

def font(size,lang='en'):
    return ImageFont.truetype(str(Path('C:/Windows/Fonts')/('msyh.ttc' if lang=='zh' else 'segoeui.ttf')),size)

def card(name,title,lines,lang):
    shot=Image.open(RAW/name).convert('RGB')
    out=Image.new('RGB',(shot.width+48,shot.height+190),BG)
    out.paste(shot,(24,76));d=ImageDraw.Draw(out)
    d.text((24,20),title,font=font(25,lang),fill=TEXT)
    for i,line in enumerate(lines):d.text((24,shot.height+94+26*i),line,font=font(18,lang),fill=MUTED)
    return out

def main():
    for lang in ('en','zh'):
        labels=('Latest-update example','Modified: start time','Edit docs / Fix tests / Update API','Fix tests / Update API / Edit docs') if lang=='en' else ('更新时间排序示例','改版：按开始时间排序','编辑文档 / 修复测试 / 更新 API','修复测试 / 更新 API / 编辑文档')
        a=card('before-'+lang+'.png',labels[0],[labels[2],'10:05 / 10:01 / 09:55'],lang)
        b=card('after-'+lang+'.png',labels[1],[labels[3],'10:00 / 09:50 / 09:10'],lang)
        comparison=Image.new('RGB',(a.width+b.width+24,a.height+72),BG)
        comparison.paste(a,(0,0));comparison.paste(b,(a.width+24,0))
        note='Real interface · fictional tasks · timestamps explained in README' if lang=='en' else '真实界面，使用虚构任务；时间依据见 README'
        ImageDraw.Draw(comparison).text((24,a.height+12),note,font=font(22,lang),fill=TEXT)
        comparison.save(ROOT/('before-after-'+lang+'.png'))
        entries=[('read-yellow-en.png','Read plan: still yellow',['Yellow follows pending implementation.']),('pinned-en.png','Pinned attention example',['Red: pinned attention. Yellow: pending plan.','Pins form a separate group; colors do not rank tasks.']),('running-en.png','A new start moves Edit docs first',['Running keeps its native spinner.','Update API still has a pending yellow plan.']),('cleared-en.png','After implementation completes',['The pending yellow indicator clears.'])] if lang=='en' else [('pinned-zh.png','已读与固定后的计划仍为黄色',['红色：固定关注；黄色：计划待实施。','固定任务另成一组，颜色不决定任务顺序。']),('running-zh.png','新开始事件使编辑文档排在最前',['运行中保留原生转圈提示。','更新 API 的待实施计划仍为黄色。']),('cleared-zh.png','实施完成后的变化',['黄色待实施标记消失。'])]
        # Keep animation one sidebar wide so native labels remain legible on phones.
        first=Image.new('RGB',(b.width,b.height+72),BG)
        first.paste(b,(0,0))
        ImageDraw.Draw(first).text((24,b.height+12),'Real interface · fictional tasks' if lang=='en' else '真实界面，使用虚构任务',font=font(22,lang),fill=TEXT)
        frames=[first]
        for name,title,lines in entries:
            c=card(name,title,lines,lang);frame=Image.new('RGB',first.size,BG)
            frame.paste(c,((frame.width-c.width)//2,0))
            ImageDraw.Draw(frame).text((24,frame.height-42),'Real interface · fictional tasks' if lang=='en' else '真实界面，使用虚构任务',font=font(22,lang),fill=TEXT)
            frames.append(frame)
        strip=Image.new('RGB',(first.width,len(frames)*first.height))
        for i,frame in enumerate(frames):strip.paste(frame,(0,i*frame.height))
        palette=strip.quantize(colors=256)
        colors=Counter()
        for name in ['after-'+lang+'.png','pinned-'+lang+'.png']:
            with Image.open(RAW/name) as shot:
                colors.update(shot.convert('RGB').crop((450,200,480,530)).getdata())
        native=[rgb for rgb,count in colors.most_common() if count>=20 and max(rgb)-min(rgb)>45][:16]
        values=palette.getpalette()
        for i,rgb in enumerate(native):values[(255-i)*3:(256-i)*3]=rgb
        palette.putpalette(values)
        converted=[frame.quantize(palette=palette,dither=Image.Dither.NONE) for frame in frames]
        output=ROOT/('demo-'+lang+'.gif')
        converted[0].save(output,save_all=True,append_images=converted[1:],duration=[6500]+[4000]*(len(frames)-1),loop=0,disposal=2,optimize=False)
        with Image.open(output) as gif:
            assert gif.n_frames==len(frames)
            for frame in ImageSequence.Iterator(gif):assert frame.size==first.size
    preview=Image.new('RGB',(1200,630),BG);d=ImageDraw.Draw(preview)
    d.text((36,40),'Codex Desktop Workflow',font=font(36),fill=TEXT)
    d.text((36,104),'26.924.2738.0 · 72 migrations · source-built repair',font=font(22),fill=MUTED)
    shot=Image.open(RAW/'pinned-en.png').convert('RGB');shot.thumbnail((365,450));preview.paste(shot,(785,160))
    for i,line in enumerate(['Start-time sorting','Yellow: pending plan','Red: pinned attention','Blue: ordinary unread','Real interface · fictional tasks']):d.text((36,190+i*62),line,font=font(27),fill=TEXT)
    preview.save(ROOT/'social-preview.png')
    (ROOT/'raw-checksums.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(RAW.glob('*.png'))},indent=2)+'\n',newline='\n')
    print('Real screenshots preserved; bilingual comparison, GIFs and preview composed.')

if __name__=='__main__':main()
