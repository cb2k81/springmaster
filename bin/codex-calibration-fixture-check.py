#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

ap=argparse.ArgumentParser()
ap.add_argument('--project-root')
a=ap.parse_args()
root=Path(a.project_root).resolve() if a.project_root else Path(__file__).resolve().parents[1]

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
