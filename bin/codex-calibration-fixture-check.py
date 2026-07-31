#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
expected={
 root/'src/test/resources/tooling/codex-calibration-v1/task-1.txt':'CALIBRATION_TASK_1=PASS\n',
 root/'src/test/resources/tooling/codex-calibration-v1/task-2.txt':'CALIBRATION_TASK_2=PASS\n',
}
changed=[]
for path,value in expected.items():
    if path.read_text(encoding='utf-8') not in {value,'TASK_1_BASELINE\n','TASK_2_BASELINE\n'}:
        changed.append(str(path))
if changed:
    print('CODEX_CALIBRATION_FIXTURE_CHECK=FAIL')
    for p in changed: print('INVALID='+p)
    sys.exit(1)
print('CODEX_CALIBRATION_FIXTURE_CHECK=PASS')
