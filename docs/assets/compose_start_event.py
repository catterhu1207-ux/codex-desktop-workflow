"""Compose external bilingual captions around preserved native screenshots."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
FONT_CANDIDATES=['/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
import os
if os.name=='nt':FONT_CANDIDATES.insert(0,str(Path(os.environ['WINDIR'])/'Fonts/msyh.ttc'))
font_path=next(p for p in FONT_CANDIDATES if Path(p).is_file())
font=ImageFont.truetype(font_path,23);small=ImageFont.truetype(font_path,18)
for language in ['en','zh']:
 frames=[]
 for index,name in enumerate(['before','after']):
  native=Image.open(ROOT/'raw'/('start-event-'+name+'.png')).convert('RGB').crop((90,90,590,660))
  # The native crop is pasted byte-for-byte; all annotations lie outside it.
  canvas=Image.new('RGB',(540,690),'#f7f7f7');draw=ImageDraw.Draw(canvas)
  labels=['Before the new turn','After the real turn starts'] if language=='en' else ['新一轮开始前','真实开始事件后']
  draw.text((20,12),labels[index],font=font,fill='#111111');canvas.paste(native,(20,58))
  note='Real interface / Fictional tasks' if language=='en' else '真实界面 / 虚构任务'
  draw.text((20,652),note,font=small,fill='#333333');frames.append(canvas)
 frames[0].save(ROOT/('start-event-'+language+'.gif'),save_all=True,append_images=frames[1:],duration=[2400,3200],loop=0)
print('Composed two native frames per language')
