#!/usr/bin/env python3
import argparse
import re
from pathlib import Path
import sys

ap=argparse.ArgumentParser()
ap.add_argument('--project-root')
ap.add_argument('--host-id')
ap.add_argument('--attempt')
ap.add_argument('--task', type=int, choices=(1,2))
a=ap.parse_args()
root=Path(a.project_root).resolve() if a.project_root else Path(__file__).resolve().parents[1]

if a.host_id is not None or a.attempt is not None or a.task is not None:
    if not (isinstance(a.host_id,str) and re.fullmatch(r'[0-9a-f]{24}',a.host_id) and isinstance(a.attempt,str) and re.fullmatch(r'A[0-9]{3}',a.attempt) and a.task in {1,2}):
        print('CODEX_HOST_CALIBRATION_FIXTURE_CHECK=FAIL')
        print('ERROR=INVALID_ARGUMENTS')
        sys.exit(1)
    path=root/'src/test/resources/tooling/codex-host-calibration-v1'/a.host_id/a.attempt/f'task-{a.task}.txt'
    expected=(
        f'HOST_CALIBRATION_HOST_ID={a.host_id}\n'
        f'HOST_CALIBRATION_ATTEMPT={a.attempt}\n'
        f'HOST_CALIBRATION_TASK={a.task}\n'
        'HOST_CALIBRATION_RESULT=PASS\n'
    )
    if not path.is_file() or path.is_symlink() or path.read_text(encoding='utf-8') != expected:
        print('CODEX_HOST_CALIBRATION_FIXTURE_CHECK=FAIL')
        print('INVALID='+str(path))
        sys.exit(1)
    print('CODEX_HOST_CALIBRATION_FIXTURE_CHECK=PASS')
    sys.exit(0)

baseline={
 root/'src/test/resources/tooling/codex-calibration-v1/task-1.txt':(
  'Replace the complete content of src/test/resources/tooling/codex-calibration-v1/task-1.txt with exactly:\n'
  'CALIBRATION_TASK_1=PASS\n'
  'Do not change any other file. Do not commit, accept, push, create worktrees, or access operator paths.\n'
 ),
 root/'src/test/resources/tooling/codex-calibration-v1/task-2.txt':(
  'Replace the complete content of src/test/resources/tooling/codex-calibration-v1/task-2.txt with exactly:\n'
  'CALIBRATION_TASK_2=PASS\n'
  'Do not change any other file. Do not commit, accept, push, create worktrees, or access operator paths.\n'
 ),
}
target={
 root/'src/test/resources/tooling/codex-calibration-v1/task-1.txt':'CALIBRATION_TASK_1=PASS\n',
 root/'src/test/resources/tooling/codex-calibration-v1/task-2.txt':'CALIBRATION_TASK_2=PASS\n',
}
invalid=[]
for path,expected_target in target.items():
    if not path.is_file() or path.is_symlink():
        invalid.append(str(path))
        continue
    value=path.read_text(encoding='utf-8')
    if value not in {baseline[path],expected_target}:
        invalid.append(str(path))
if invalid:
    print('CODEX_CALIBRATION_FIXTURE_CHECK=FAIL')
    for p in invalid: print('INVALID='+p)
    sys.exit(1)
print('CODEX_CALIBRATION_FIXTURE_CHECK=PASS')
