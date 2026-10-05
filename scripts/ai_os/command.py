"""AI-OS command adapter for the authorized Amazon staging checkout."""
from pathlib import Path
import json
import subprocess
import sys

REPOSITORY = Path('/Users/jpg/.codex/.chatgpt-projects/g-p-6ab52c1082ac8191b982f18bdeac226b/amazon-site')

def run(arguments):
    if not arguments or arguments[0] not in {'status','draft','audit'}:
        raise SystemExit('Usage: ai-os amazon status | draft cuyabeno | audit')
    action=arguments[0]
    if action=='status':
        reports=sorted((REPOSITORY/'planning/ai-os/runs').glob('*/*/status.json'))
        print(json.dumps([json.loads(p.read_text()) for p in reports],indent=2))
        return
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=REPOSITORY,text=True).strip()
    if branch != 'staging':
        raise SystemExit('Amazon adapter requires staging branch')
    if action=='draft':
        if arguments != ['draft','cuyabeno']:
            raise SystemExit('Pilot authorizes one pair: cuyabeno')
        command=[sys.executable,str(REPOSITORY/'scripts/ai_os/pilot.py'),'cuyabeno']
    else:
        command=[sys.executable,str(REPOSITORY/'scripts/ai_os/audit.py')]
    result=subprocess.run(command,cwd=REPOSITORY)
    if result.returncode:
        raise SystemExit(result.returncode)
