"""Read-only runtime evidence plus 30 health requests and one 404 event."""
import urllib.request,urllib.parse,urllib.error,json,time,subprocess,datetime
from pathlib import Path
root=Path(__file__).resolve().parents[1]
env=dict(line.split('=',1) for line in (root/'.env').read_text().splitlines() if '=' in line)
def get(url):
 with urllib.request.urlopen(url,timeout=20)as r:return json.load(r)
def prom(q):return get('http://127.0.0.1:'+env['PROM_PORT']+'/api/v1/query?'+urllib.parse.urlencode({'query':q}))['data']['result']
def compose(*args):return subprocess.check_output(['docker','compose','-f','compose.yaml','-f','compose.monitoring.yaml','-f','compose.logging.yaml',*args],cwd=root,text=True,encoding='utf-8')
def main():
 before={k:float(prom(k)[0]['value'][1])for k in ['nginx_http_requests_total','mysql_global_status_queries']}
 for _ in range(30):
  with urllib.request.urlopen('http://127.0.0.1:'+env['WEB_PORT']+'/health',timeout=10)as r:assert r.status==200
  time.sleep(.1)
 try:urllib.request.urlopen('http://127.0.0.1:'+env['WEB_PORT']+'/evidence-not-found')
 except urllib.error.HTTPError as e:assert e.code==404
 for _ in range(10):
  after={k:float(prom(k)[0]['value'][1])for k in before}
  if all(after[k]>before[k]for k in before):break
  time.sleep(3)
 assert all(after[k]>before[k]for k in before),(before,after)
 targets=get('http://127.0.0.1:'+env['PROM_PORT']+'/api/v1/targets')['data']['activeTargets']
 assert len(targets)==4 and all(t['health']=='up'for t in targets)
 qs=['mysql_up','nginx_up','mysql_global_status_threads_connected','rate(nginx_http_requests_total[2m])','rate(mysql_global_status_queries[2m])','container_memory_working_set_bytes{image!="",name=~"attendance27-.*"}','100 * sum by (name)(rate(container_cpu_usage_seconds_total{image!="",name=~"attendance27-.*"}[2m]))','sum by(name)(rate(container_network_receive_bytes_total{image!="",name=~"attendance27-.*"}[2m]))']
 metrics={q:prom(q)for q in qs};assert all(metrics.values()),'Metric data missing'
 assert metrics['mysql_up'][0]['value'][1]=='1' and metrics['nginx_up'][0]['value'][1]=='1'
 logql=['{project="attendance27",job="nginx"} | json','{project="attendance27",job="nginx"} | json | status >= 400','{project="attendance27",job="app"} | json | event =~ "login_.*|check_in|check_out"']
 logs=[]
 for q in logql:
  result=get('http://127.0.0.1:'+env['LOKI_PORT']+'/loki/api/v1/query_range?'+urllib.parse.urlencode({'query':q,'start':str(int((time.time()-3600)*1e9)),'end':str(int(time.time()*1e9)),'limit':100}))
  count=sum(len(s['values'])for s in result['data']['result']);assert count>0,q
  logs.append({'query':q,'returned_lines':count,'response':result})
 ids=compose('ps','-q').split();raw=json.loads(subprocess.check_output(['docker','inspect',*ids],text=True,encoding='utf-8'))
 hardening=[]
 for c in raw:
  hardening.append({'service':c['Config']['Labels']['com.docker.compose.service'],'name':c['Name'],'configured_user':c['Config']['User'],'read_only':c['HostConfig']['ReadonlyRootfs'],'privileged':c['HostConfig']['Privileged'],'cap_drop':c['HostConfig']['CapDrop'],'cap_add':c['HostConfig']['CapAdd'],'security_opt':c['HostConfig']['SecurityOpt'],'ports':c['NetworkSettings']['Ports'],'networks':list(c['NetworkSettings']['Networks']),'processes':subprocess.check_output(['docker','top',c['Id'],'-eo','uid,pid,comm'],text=True).strip()})
 network=json.loads(subprocess.check_output(['docker','network','inspect','attendance27_database'],text=True))[0];assert network['Internal']
 db=[c for c in hardening if c['service']=='mysql'][0];assert all(v is None for v in db['ports'].values())
 grants=compose('exec','-T','mysql','sh','-c','MYSQL_PWD="$MYSQL_PASSWORD" mysql -uattendance_app -N -e "SHOW GRANTS FOR CURRENT_USER"').strip()
 assert 'SELECT, INSERT, UPDATE, DELETE' in grants and 'ALL PRIVILEGES'not in grants
 out={'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'targets':[{'job':x['labels']['job'],'health':x['health'],'last_error':x['lastError']}for x in targets],'load_check':{'requests':30,'before':before,'after':after},'metrics':metrics,'logql':logs,'hardening':hardening,'database_internal':network['Internal'],'database_grants':grants}
 (root/'docs/evidence/runtime.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 print('PASS: 4 targets UP,',len(metrics),'metric queries populated, counters increased, 3 LogQL queries returned logs. Hardening verified.')
if __name__=='__main__':main()
