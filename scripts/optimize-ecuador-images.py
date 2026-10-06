"""Reduce JPEG transfer weight without changing aspect ratio or framing (macOS sips)."""
from pathlib import Path
import subprocess,tempfile,json,hashlib
results=[]
for folder in ['ecuador','global']:
 for p in Path('src/assets/images',folder).glob('*.jpg'):
  original=p.read_bytes()
  if len(original)<200000:continue
  with tempfile.TemporaryDirectory() as directory:
   out=Path(directory)/p.name
   subprocess.run(['sips','-Z','1600','-s','formatOptions','75',str(p),'--out',str(out)],check=True,capture_output=True)
   candidate=out.read_bytes()
   if len(candidate)<len(original):
    p.write_bytes(candidate)
    results.append({'asset':str(p),'before':len(original),'after':len(candidate),'original_sha256':hashlib.sha256(original).hexdigest()})
report={'method':'JPEG quality 75; maximum dimension 1600px; aspect ratio and framing unchanged','rollback_commit':'2dd2dc7','files':results,'bytes_saved':sum(r['before']-r['after'] for r in results)}
Path('planning/ai-os/image-resize-optimization.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'images_optimized':len(results),'bytes_saved':report['bytes_saved']}))
