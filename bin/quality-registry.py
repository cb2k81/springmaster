#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from typing import Any
CATALOG_SCHEMA='springmaster.quality-rule-catalog.v1'; GATE_SCHEMA='springmaster.gate-registry.v1'; REPORT_SCHEMA='springmaster.quality-registry-report.v1'
RID=re.compile(r'^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$'); GID=re.compile(r'^[a-z][a-z0-9]*(?:-[a-z0-9]+)+-v[0-9]+$')
class ToolError(RuntimeError):
 def __init__(self,code,msg,path=None): super().__init__(msg); self.code=code; self.msg=msg; self.path=path

def load(path:Path,schema:str)->dict[str,Any]:
 if not path.is_file(): raise ToolError('CONTRACT_MISSING',f'Missing contract: {path}',str(path))
 try: v=json.loads(path.read_text())
 except Exception as e: raise ToolError('CONTRACT_INVALID_JSON',f'Cannot parse {path}: {e}',str(path))
 if not isinstance(v,dict) or v.get('schemaVersion')!=schema: raise ToolError('CONTRACT_SCHEMA_UNSUPPORTED',f'Expected {schema}',str(path))
 return v

def finding(rule,code,path,msg,**details):
 x={'ruleId':rule,'code':code,'path':path,'message':msg}
 if details:x['details']=details
 return x

def headings(path:Path)->set[str]:
 return {re.sub(r'^#+\s*','',line.strip()) for line in path.read_text().splitlines() if re.match(r'^#{2,3}\s+',line)}

def validate(root:Path,c:dict,g:dict)->list[dict]:
 f=[]; rules=c.get('rules'); gates=g.get('gates')
 if not isinstance(rules,list): return [finding('QREG-CATALOG-001','RULES_INVALID','quality-rule-catalog.json','rules must be a list')]
 if not isinstance(gates,list): return [finding('QREG-GATE-001','GATES_INVALID','gate-registry.json','gates must be a list')]
 rmap={}; gmap={}
 allowed={k:set(c.get(k,[])) for k in ['allowedLayers','allowedTestabilityClasses','allowedSeverities','allowedLifecycles','allowedEnforcementModes']}
 for i,r in enumerate(rules):
  p=f'quality-rule-catalog.json#/rules/{i}'
  if not isinstance(r,dict): f.append(finding('QREG-CATALOG-001','RULE_INVALID',p,'rule must be an object')); continue
  rid=r.get('ruleId')
  if not isinstance(rid,str) or not RID.fullmatch(rid): f.append(finding('QREG-IDENTITY-001','RULE_ID_INVALID',p,'invalid ruleId'))
  elif rid in rmap: f.append(finding('QREG-IDENTITY-001','RULE_ID_DUPLICATE',p,'duplicate ruleId',ruleId=rid))
  else:rmap[rid]=r
  if 'normativeText' in r: f.append(finding('QREG-CATALOG-001','NORMATIVE_TEXT_FORBIDDEN',p,'catalog must not duplicate normative rule text'))
  for field,key in [('layer','allowedLayers'),('testabilityClass','allowedTestabilityClasses'),('defaultSeverity','allowedSeverities'),('lifecycle','allowedLifecycles')]:
   if r.get(field) not in allowed[key]: f.append(finding('QREG-CATALOG-001','VOCABULARY_INVALID',p,f'{field} is invalid',field=field,actual=r.get(field)))
  modes=r.get('supportedEnforcementModes')
  if not isinstance(modes,list) or not modes or any(x not in allowed['allowedEnforcementModes'] for x in modes): f.append(finding('QREG-CATALOG-001','ENFORCEMENT_MODES_INVALID',p,'supportedEnforcementModes invalid'))
  src=r.get('normativeSource')
  if not isinstance(src,dict): f.append(finding('QREG-SOURCE-001','SOURCE_INVALID',p,'normativeSource missing')); continue
  sp=src.get('path'); sec=src.get('section'); fp=root/sp if isinstance(sp,str) else None
  if fp is None or not fp.is_file(): f.append(finding('QREG-SOURCE-001','SOURCE_PATH_MISSING',p,'normative source path missing',source=sp))
  elif not isinstance(sec,str) or sec not in headings(fp): f.append(finding('QREG-SOURCE-001','SOURCE_SECTION_MISSING',p,'normative source section missing',source=sp,section=sec))
  gids=r.get('gateIds',[])
  if not isinstance(gids,list): f.append(finding('QREG-REFERENCE-001','GATE_REFS_INVALID',p,'gateIds must be a list'))
  if r.get('lifecycle') in {'implemented-report-only','qualified-report-only','strict'} and not gids and not r.get('plannedGateId'):
   f.append(finding('QREG-REFERENCE-001','IMPLEMENTED_RULE_UNMAPPED',p,'implemented rule needs gateIds or plannedGateId'))
 for i,x in enumerate(gates):
  p=f'gate-registry.json#/gates/{i}'
  if not isinstance(x,dict): f.append(finding('QREG-GATE-001','GATE_INVALID',p,'gate must be object')); continue
  gid=x.get('gateId')
  if not isinstance(gid,str) or not GID.fullmatch(gid): f.append(finding('QREG-IDENTITY-001','GATE_ID_INVALID',p,'invalid gateId'))
  elif gid in gmap:f.append(finding('QREG-IDENTITY-001','GATE_ID_DUPLICATE',p,'duplicate gateId',gateId=gid))
  else:gmap[gid]=x
  if x.get('defaultEnforcementMode')!='report-only' or x.get('supportedEnforcementModes')!=['report-only']:
   f.append(finding('QREG-GATE-001','REPORT_ONLY_CONTRACT_INVALID',p,'current registry gates must remain report-only'))
  if x.get('readOnly') is not True or x.get('sideEffects')!=['report-files-only']:
   f.append(finding('QREG-GATE-001','READ_ONLY_CONTRACT_INVALID',p,'gate must be read-only with report-only side effects'))
  for field in ['entrypoint','fixtureEntrypoint','selfcheckEntrypoint']:
   rel=x.get(field)
   if not isinstance(rel,str) or not (root/rel).is_file(): f.append(finding('QREG-GATE-001','ENTRYPOINT_MISSING',p,f'{field} missing',value=rel))
  for rel in x.get('inputContracts',[]):
   if not isinstance(rel,str) or not (root/rel).is_file(): f.append(finding('QREG-GATE-001','INPUT_CONTRACT_MISSING',p,'input contract missing',value=rel))
 for rid,r in rmap.items():
  for gid in r.get('gateIds',[]):
   if gid not in gmap: f.append(finding('QREG-REFERENCE-001','UNKNOWN_GATE_REFERENCE',rid,'rule references unknown gate',gateId=gid))
   elif rid not in gmap[gid].get('ruleIds',[]): f.append(finding('QREG-REFERENCE-001','NONRECIPROCAL_GATE_REFERENCE',rid,'gate does not reference rule',gateId=gid))
 for gid,x in gmap.items():
  for rid in x.get('ruleIds',[]):
   if rid not in rmap: f.append(finding('QREG-REFERENCE-001','UNKNOWN_RULE_REFERENCE',gid,'gate references unknown rule',ruleId=rid))
   elif gid not in rmap[rid].get('gateIds',[]): f.append(finding('QREG-REFERENCE-001','NONRECIPROCAL_RULE_REFERENCE',gid,'rule does not reference gate',ruleId=rid))
 return f

def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--project-root',type=Path,default=Path(__file__).resolve().parents[1]); ap.add_argument('--contract-root',type=Path); ap.add_argument('--out',type=Path); ap.add_argument('--check',action='store_true'); ap.add_argument('operation',choices=['catalog','gates','all'],default='all',nargs='?'); a=ap.parse_args()
 root=a.project_root.resolve(); cr=(a.contract_root or root/'contracts/governance/quality').resolve(); fs=[]; tes=[]; details={}
 try:
  c=load(cr/'quality-rule-catalog.json',CATALOG_SCHEMA); g=load(cr/'gate-registry.json',GATE_SCHEMA)
  fs=validate(root,c,g)
  if a.operation=='catalog': fs=[x for x in fs if not x['path'].startswith('gate-registry')]
  elif a.operation=='gates': fs=[x for x in fs if not x['path'].startswith('quality-rule-catalog')]
  details={'ruleCount':len(c.get('rules',[])),'gateCount':len(g.get('gates',[]))}
 except ToolError as e:
  t={'code':e.code,'message':e.msg};
  if e.path:t['path']=e.path
  tes=[t]
 status='TOOL_ERROR' if tes else ('FINDINGS' if fs else 'PASS')
 report={'schemaVersion':REPORT_SCHEMA,'status':status,'operation':a.operation,'findingCount':len(fs),'toolErrorCount':len(tes),'details':details,'findings':fs,'toolErrors':tes}
 text=json.dumps(report,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n'
 if a.out:a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(text)
 else:sys.stdout.write(text)
 print(f'QUALITY_REGISTRY={status}',file=sys.stderr)
 if tes:return 2
 if fs and a.check:return 1
 return 0
if __name__=='__main__': raise SystemExit(main())
