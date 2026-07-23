#!/usr/bin/env python3
"""Validate Springmaster test suites, fixtures and sealed test inventory."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from typing import Any

REPORT_SCHEMA="springmaster.test-contracts-report.v1"
FILES={
 "suites":("test-suite-contract.json","springmaster.test-suite-contract.v1"),
 "fixtures":("test-fixture-contract.json","springmaster.test-fixture-contract.v1"),
 "inventory":("test-inventory-baseline.json","springmaster.test-inventory-baseline.v1"),
}
class ToolError(RuntimeError):
 def __init__(self,code:str,message:str,path:str|None=None): super().__init__(message); self.code=code; self.message=message; self.path=path

def load_json(path:Path,code="JSON_READ_ERROR") -> Any:
 if not path.is_file(): raise ToolError("FILE_MISSING",f"Required JSON file is missing: {path}",str(path))
 try:return json.loads(path.read_text(encoding="utf-8"))
 except Exception as exc: raise ToolError(code,f"Cannot parse JSON file {path}: {exc}",str(path)) from exc

def load_contracts(root:Path):
 out={}
 for key,(name,schema) in FILES.items():
  p=root/name; value=load_json(p,"CONTRACT_PARSE_ERROR")
  if not isinstance(value,dict): raise ToolError("CONTRACT_INVALID_SHAPE",f"Contract must contain a JSON object: {p}",str(p))
  if value.get("schemaVersion")!=schema: raise ToolError("CONTRACT_SCHEMA_MISMATCH",f"Expected schema {schema}, got {value.get('schemaVersion')!r}",str(p))
  out[key]=value
 return out

def issue(code,path,message,**details):
 x={"code":code,"path":path,"message":message}
 if details:x["details"]=details
 return x

def duplicates(values):
 seen=set(); out=[]
 for v in values:
  if v in seen and v not in out: out.append(v)
  seen.add(v)
 return out

def ids(items,field="id"):
 return [x.get(field) for x in items if isinstance(x,dict) and isinstance(x.get(field),str)] if isinstance(items,list) else []

def source_inventory(project:Path):
 java=sorted(p.relative_to(project).as_posix() for p in (project/"src/test/java").rglob("*.java")) if (project/"src/test/java").exists() else []
 tooling=[]
 bindir=project/"bin"
 if bindir.exists():
  for p in bindir.glob("*.sh"):
   n=p.name
   if n.endswith("-it.sh") or "selfcheck" in n or "acceptance" in n or "regression" in n: tooling.append(p.relative_to(project).as_posix())
 upd=project/"platform/update/tests"
 if upd.exists(): tooling += [p.relative_to(project).as_posix() for p in upd.glob("*.sh")]
 fixtures=sorted(p.relative_to(project).as_posix() for p in (project/"src/test/resources/tooling").rglob("*") if p.is_file()) if (project/"src/test/resources/tooling").exists() else []
 return {"java":java,"tooling":sorted(tooling),"fixtures":fixtures}

def contract_findings(c,project:Path):
 f=[]; s=c["suites"]; fx=c["fixtures"]; inv=c["inventory"]
 runners=ids(s.get("runners")); suites=ids(s.get("suites"))
 for v in duplicates(runners):f.append(issue("DUPLICATE_RUNNER","test-suite-contract.json",f"Duplicate runner: {v}"))
 for v in duplicates(suites):f.append(issue("DUPLICATE_SUITE","test-suite-contract.json",f"Duplicate suite: {v}"))
 allowed_profiles=set(s.get("allowedEngineeringProfiles",[])); allowed_modes=set(s.get("allowedEnforcementModes",[])); allowed_runtime=set(s.get("runtimeClasses",[]))
 for item in s.get("suites",[]):
  if item.get("runnerId") not in runners:f.append(issue("UNKNOWN_RUNNER","test-suite-contract.json",f"Suite {item.get('id')!r} references unknown runner {item.get('runnerId')!r}"))
  for p in item.get("engineeringProfiles",[]):
   if p not in allowed_profiles:f.append(issue("UNKNOWN_PROFILE","test-suite-contract.json",f"Suite {item.get('id')!r} references unknown profile {p!r}"))
  if not item.get("changeClasses"):f.append(issue("SUITE_CHANGE_CLASSES_MISSING","test-suite-contract.json",f"Suite {item.get('id')!r} has no changeClasses"))
  if item.get("enforcementMode") not in allowed_modes:f.append(issue("INVALID_ENFORCEMENT","test-suite-contract.json",f"Suite {item.get('id')!r} uses unsupported enforcement mode"))
  if item.get("runtimeClass") not in allowed_runtime:f.append(issue("INVALID_RUNTIME_CLASS","test-suite-contract.json",f"Suite {item.get('id')!r} uses unknown runtime class"))
  if not item.get("scopePaths"):f.append(issue("SUITE_SCOPE_MISSING","test-suite-contract.json",f"Suite {item.get('id')!r} has no scopePaths"))
 for comp in s.get("composition",[]):
  if comp.get("suiteId") not in suites:f.append(issue("COMPOSITION_SUITE_UNKNOWN","test-suite-contract.json","Composition owner suite is unknown"))
  for child in comp.get("composes",[]):
   if child not in suites:f.append(issue("COMPOSITION_CHILD_UNKNOWN","test-suite-contract.json",f"Unknown composed suite: {child}"))
 pom=(project/"pom.xml").read_text(encoding="utf-8") if (project/"pom.xml").is_file() else ""
 mb=s.get("mavenBaseline",{})
 failsafe_actual="maven-failsafe-plugin" in pom
 if bool(mb.get("failsafeImplemented")) != failsafe_actual:f.append(issue("FAILSAFE_BASELINE_MISMATCH","test-suite-contract.json","Failsafe implementation claim differs from pom.xml"))
 if mb.get("coverageThresholds") not in ([],None):f.append(issue("COVERAGE_THRESHOLD_PREMATURE","test-suite-contract.json","Coverage thresholds are forbidden while coverage decision is unresolved"))
 if mb.get("coverageDecision")!="unresolved":f.append(issue("COVERAGE_DECISION_PREMATURE","test-suite-contract.json","Coverage decision must remain unresolved in v1 baseline"))
 if mb.get("coverageTool") is not None:f.append(issue("COVERAGE_TOOL_PREMATURE","test-suite-contract.json","Coverage tool must remain null until separately decided"))
 # external profile/class references
 profile_path=project/s.get("profileSources",{}).get("engineeringProfiles","")
 class_path=project/s.get("profileSources",{}).get("changeClasses","")
 ep=load_json(profile_path,"REFERENCE_CONTRACT_PARSE_ERROR"); ec=load_json(class_path,"REFERENCE_CONTRACT_PARSE_ERROR")
 actual_profiles=set(ids(ep.get("profiles"))); actual_classes=set(ids(ec.get("changeClasses")))
 if allowed_profiles!=actual_profiles:f.append(issue("PROFILE_SOURCE_MISMATCH","test-suite-contract.json","allowedEngineeringProfiles differs from engineering profile contract"))
 for item in s.get("suites",[]):
  for class_id in item.get("changeClasses",[]):
   if class_id not in actual_classes:f.append(issue("UNKNOWN_CHANGE_CLASS","test-suite-contract.json",f"Suite {item.get('id')!r} references unknown change class {class_id!r}"))
 # fixture semantics
 types=set(ids(fx.get("fixtureTypes"))); paths=[]
 for e in fx.get("fixtureEntries",[]):
  p=e.get("path"); paths.append(p)
  if e.get("fixtureType") not in types:f.append(issue("UNKNOWN_FIXTURE_TYPE","test-fixture-contract.json",f"Unknown fixture type for {p!r}"))
  if not any(isinstance(p,str) and (p==r or p.startswith(r+"/")) for r in fx.get("canonicalSourceRoots",[])):f.append(issue("FIXTURE_OUTSIDE_CANONICAL_ROOT","test-fixture-contract.json",f"Fixture outside canonical roots: {p!r}"))
  if not e.get("consumers"):f.append(issue("FIXTURE_CONSUMER_MISSING","test-fixture-contract.json",f"Fixture has no consumer: {p!r}"))
  for consumer in e.get("consumers",[]):
   if not (project/consumer).is_file():f.append(issue("FIXTURE_CONSUMER_NOT_FOUND","test-fixture-contract.json",f"Fixture consumer does not exist: {consumer}"))
  if e.get("fixtureType")=="golden-json" and e.get("mutationPolicy")!="reviewed-contract-change-only":f.append(issue("GOLDEN_MUTATION_POLICY_INVALID","test-fixture-contract.json",f"Golden fixture has unsafe mutation policy: {p!r}"))
 for v in duplicates(paths):f.append(issue("DUPLICATE_FIXTURE_ENTRY","test-fixture-contract.json",f"Duplicate fixture path: {v}"))
 # inventory refs
 for section in ["javaTests","toolingTests"]:
  vals=inv.get(section,[]); pths=[x.get("path") for x in vals if isinstance(x,dict)]
  for v in duplicates(pths):f.append(issue("DUPLICATE_INVENTORY_PATH","test-inventory-baseline.json",f"Duplicate inventory path: {v}"))
  for e in vals:
   if e.get("suiteId") not in suites:f.append(issue("INVENTORY_SUITE_UNKNOWN","test-inventory-baseline.json",f"Unknown suite for {e.get('path')!r}"))
 return f

def inventory_findings(c,project:Path):
 f=[]; inv=c["inventory"]; actual=source_inventory(project)
 registered={
  "java":sorted(x["path"] for x in inv.get("javaTests",[]) if isinstance(x,dict) and isinstance(x.get("path"),str)),
  "tooling":sorted(x["path"] for x in inv.get("toolingTests",[]) if isinstance(x,dict) and isinstance(x.get("path"),str)),
  "fixtures":sorted(x["path"] for x in inv.get("sourceFixtures",[]) if isinstance(x,dict) and isinstance(x.get("path"),str)),
 }
 for kind in ["java","tooling","fixtures"]:
  for p in sorted(set(actual[kind])-set(registered[kind])):f.append(issue("UNREGISTERED_"+kind.upper(),p,f"Unregistered {kind} artifact"))
  for p in sorted(set(registered[kind])-set(actual[kind])):f.append(issue("REGISTERED_"+kind.upper()+"_MISSING",p,f"Registered {kind} artifact is missing"))
 summary=inv.get("summary",{})
 expected={"javaTestClassCount":len(registered["java"]),"toolingEntrypointCount":len(registered["tooling"]),"sourceFixtureCount":len(registered["fixtures"])}
 for key,value in expected.items():
  if summary.get(key)!=value:f.append(issue("INVENTORY_SUMMARY_MISMATCH","test-inventory-baseline.json",f"{key} mismatch",expected=value,actual=summary.get(key)))
 return f

def fixture_findings(c,project:Path):
 f=[]; fx=c["fixtures"]
 for e in fx.get("fixtureEntries",[]):
  p=project/e.get("path","")
  if not p.is_file():continue
  try:data=json.loads(p.read_text(encoding="utf-8"))
  except Exception as exc:f.append(issue("FIXTURE_JSON_INVALID",e.get("path",""),f"Fixture JSON cannot be parsed: {exc}"));continue
  if e.get("fixtureType")=="expected-case-catalog":
   cases=data.get("cases") if isinstance(data,dict) else None
   if not isinstance(cases,list) or not cases:f.append(issue("EXPECTED_CASES_EMPTY",e.get("path",""),"Expected-case catalog must contain cases"));continue
   exits={x.get("expectedExit") for x in cases if isinstance(x,dict)}
   missing=sorted({0,1,2}-exits)
   if missing:f.append(issue("EXPECTED_CASE_CLASS_MISSING",e.get("path",""),"Expected-case catalog must cover pass, finding and tool-error exits",missing=missing))
 return f

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--project-root",type=Path,default=Path(__file__).resolve().parents[1]); ap.add_argument("--contract-root",type=Path); ap.add_argument("--out",type=Path); ap.add_argument("--check",action="store_true"); ap.add_argument("operation",choices=["contracts","inventory","fixtures","all"],nargs="?",default="all"); a=ap.parse_args()
 project=a.project_root.resolve(); root=(a.contract_root or project/"contracts/governance/testing").resolve(); findings=[]; errors=[]; details={}
 try:
  c=load_contracts(root)
  if a.operation in ("contracts","all"):findings+=contract_findings(c,project)
  if a.operation in ("inventory","all"):findings+=inventory_findings(c,project)
  if a.operation in ("fixtures","all"):findings+=fixture_findings(c,project)
  details={"suiteCount":len(c["suites"].get("suites",[])),"javaTestClassCount":len(c["inventory"].get("javaTests",[])),"toolingEntrypointCount":len(c["inventory"].get("toolingTests",[])),"sourceFixtureCount":len(c["inventory"].get("sourceFixtures",[]))}
 except ToolError as e:
  x={"code":e.code,"message":e.message};
  if e.path:x["path"]=e.path
  errors=[x]
 status="TOOL_ERROR" if errors else ("FINDINGS" if findings else "PASS")
 report={"schemaVersion":REPORT_SCHEMA,"status":status,"operation":a.operation,"findingCount":len(findings),"toolErrorCount":len(errors),"details":details,"findings":findings,"toolErrors":errors}
 text=json.dumps(report,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n"
 if a.out:a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(text,encoding="utf-8")
 else:sys.stdout.write(text)
 print(f"TEST_CONTRACTS={status}",file=sys.stderr)
 if errors:return 2
 if findings and a.check:return 1
 return 0
if __name__=="__main__":raise SystemExit(main())
