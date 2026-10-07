"""Apply the owner's reviewed image selections to both language routes."""
import re,json,html
from pathlib import Path
R=Path(__file__).resolve().parents[2]
P=R/'planning/ai-os/peru-image-update.json'
def apply():
 spec=json.loads(P.read_text())
 for lang in ['en','es']:
  for p in (R/'src/pages'/lang/'peru').rglob('index.html'):
   s=p.read_text()
   route='/peru/' if p.parent.name=='peru' else '/peru/'+p.parent.name+'/'
   if lang=='es':route=re.search(r'data-language-pair="([^"]+)"',s)[1]
   selected=spec['pages'][route];i=0;oldhero=re.search(r'<img[^>]*src="([^"]+)"',s)[1]
   def replace(m):
    nonlocal i
    name=selected[i];im=spec['images'][name];alt=im['alt'][lang];hero=i==0;i+=1
    portrait=' peru-photo--wildlife' if im['height']>im['width'] else ''
    return '<figure class="peru-photo'+portrait+'"><img src="'+im['src']+'" width="'+str(im['width'])+'" height="'+str(im['height'])+'" alt="'+html.escape(alt,quote=True)+'" '+('fetchpriority="high"' if hero else 'loading="lazy"')+' decoding="async"></figure>'
   s=re.sub(r'<figure\b[^>]*>.*?</figure>',replace,s,flags=re.S)
   assert i==len(selected),(p,i,len(selected))
   s=s.replace(oldhero,spec['images'][selected[0]]['src'])
   p.write_text(s)
if __name__=='__main__':apply()
