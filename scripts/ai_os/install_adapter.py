"""Install a narrow AI-OS CLI adapter, preserving existing changes."""
import hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2]
aios=Path('/Users/jpg/AI/ai-os')
cli=aios/'src/ai_os/cli.py'
command=aios/'src/ai_os/commands/amazon.py'
source=cli.read_text()
if 'from ai_os.commands import amazon' not in source:
    anchor='from ai_os.status import show_status'
    if source.count(anchor)!=1 or source.count('    "pricing": pricing.run,')!=1:
        raise SystemExit('CLI structure changed; manual review required')
    backup=root/'planning/ai-os/installation'
    backup.mkdir(parents=True,exist_ok=True)
    (backup/'cli-before.py').write_text(source)
    source=source.replace(anchor,'from ai_os.commands import amazon\n'+anchor)
    source=source.replace('    "pricing": pricing.run,','    "amazon": amazon.run,\n    "pricing": pricing.run,')
    staged=(root/'scripts/ai_os/command.py').read_text()
    if command.exists() and command.read_text()!=staged:
        raise SystemExit('Existing adapter differs; refusing to overwrite')
    command.write_text(staged)
    cli.write_text(source)
    (backup/'manifest.json').write_text('{"installed":true,"runtime_restart_required":false}\n')
    print('Installed ai-os amazon adapter; existing CLI changes preserved')
else:
    print('Adapter already registered')
