"""Record a song's first addition to the main branch, never its last edit."""
import ast
import json
import re
import subprocess
from pathlib import Path

def added_dates(log):
    result = {}
    date = None
    for line in log.splitlines():
        if line.startswith('@@'):
            date = line[2:].strip()
        elif date:
            match = re.fullmatch(r'A\s+dados/musicas/(\d+)\.txt', line.strip())
            if match:
                result.setdefault(match.group(1), date)
    return result

def main():
    target = Path('api/catalog_dates.py')
    existing = {}
    if target.exists():
        existing = ast.literal_eval(target.read_text(encoding='utf-8').split('ADDED_AT = ', 1)[1])
    history = subprocess.check_output(['git','log','--first-parent','--reverse','--diff-filter=A','--no-renames','--format=@@%cI','--name-status','--','dados/musicas'],text=True,encoding='utf-8')
    for key, date in added_dates(history).items():
        existing.setdefault(key,date)
    target.write_text('# Generated first-addition dates; edits must never reset these dates.\nADDED_AT = '+json.dumps(existing,sort_keys=True,indent=2)+'\n',encoding='utf-8')

if __name__ == '__main__':
    main()

