"""HTTP tests against real Nginx/Node/MySQL. No mocks. Creates a disabled QA account."""
import json,urllib.request,urllib.error,http.cookiejar,secrets,subprocess,time,concurrent.futures
from pathlib import Path
root=Path(__file__).resolve().parents[1]
env=dict(line.split('=',1) for line in (root/'.env').read_text().splitlines() if '=' in line)
base='http://127.0.0.1:'+env['WEB_PORT']; results=[]
class Client:
 def __init__(self):
  self.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
  self.csrf=self.call('session')[1]['csrf']
 def call(self,path,method='GET',body=None,csrf=True):
  req=urllib.request.Request(base+'/api/'+path,data=json.dumps(body).encode() if body is not None else None,method=method,headers={'Content-Type':'application/json',**({'X-CSRF-Token':self.csrf} if csrf and hasattr(self,'csrf') else {})})
  try:
   with self.opener.open(req,timeout=15)as r:return r.status,json.load(r)
  except urllib.error.HTTPError as e:return e.code,json.load(e)
 def login(self,email,password):
  status,data=self.call('login','POST',{'email':email,'password':password});assert status==200,(status,data);self.csrf=data['csrf']
def check(name,ok,detail=''):
 assert ok,(name,detail)
 results.append({'test':name,'result':'PASS','detail':detail});print('PASS',name)
def main():
 a=Client();check('Unauthenticated history denied',a.call('attendance')[0]==401)
 check('CSRF missing denied',a.call('login','POST',{'email':'admin@attendance.local','password':'wrong'},csrf=False)[0]==403)
 check('Wrong password denied',a.call('login','POST',{'email':'admin@attendance.local','password':'incorrectpassword'})[0]==401)
 a.login('admin@attendance.local',env['ADMIN_PASSWORD']);check('Admin authentication',True)
 suffix=secrets.token_hex(3);pw=secrets.token_hex(16)
 u={'code':'QA_'+suffix,'name':'Nhân sự kiểm thử '+suffix,'email':suffix+'@example.test','role':'employee','password':pw}
 status,data=a.call('users','POST',u);check('Create employee in real database',status==201);uid=data['id']
 check('Duplicate employee rejected',a.call('users','POST',u)[0]==409)
 u['name']='Kiểm thử tích hợp '+suffix;u['active']=True
 check('Edit employee',a.call('users/'+str(uid),'PUT',u)[0]==200)
 check('Read edited employee',any(x['id']==uid and x['name']==u['name'] for x in a.call('users')[1]))
 e=Client();e.login(u['email'],pw)
 check('Employee admin endpoint denied',e.call('users')[0]==403)
 check('Invalid shift rejected',a.call('shifts','POST',{'name':'Bad','start_time':'22:00','end_time':'06:00'})[0]==400)
 s={'name':'Ca kiểm thử '+suffix,'start_time':'09:00','end_time':'11:00'}
 status,data=a.call('shifts','POST',s);check('Create shift',status==201);sid=data['id']
 s['name']+=' sửa';check('Edit shift',a.call('shifts/'+str(sid),'PUT',s)[0]==200)
 check('Delete unused shift',a.call('shifts/'+str(sid),'DELETE')[0]==200)
 # Independent sessions, same account, simultaneous requests test transaction/unique constraint.
 e2=Client();e2.login(u['email'],pw)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as ex:codes=list(ex.map(lambda c:c.call('check-in','POST',{'shift_id':1})[0],[e,e2]))
 check('Concurrent check-in exactly once',sorted(codes)==[201,409],str(sorted(codes)))
 rows=e.call('attendance')[1];check('Employee history isolation',bool(rows) and all(x['user_id']==uid for x in rows));aid=rows[0]['id']
 check('Referenced shift deletion denied',a.call('shifts/1','DELETE')[0]==409)
 check('Other user cannot check out',a.call('check-out','POST',{'id':aid})[0]==409)
 check('Check out own attendance',e.call('check-out','POST',{'id':aid})[0]==200)
 check('Duplicate check out denied',e.call('check-out','POST',{'id':aid})[0]==409)
 check('Same shift same day duplicate denied',e.call('check-in','POST',{'shift_id':1})[0]==409)
 check('SQL injection login rejected',e.call('login','POST',{'email':"' OR 1=1 --",'password':pw})[0]==401)
 check('Deactivate employee',a.call('users/'+str(uid),'DELETE')[0]==200)
 check('Revoked account existing session denied',e.call('attendance')[0]==401)
 check('Cannot deactivate self',a.call('users/1','DELETE')[0]==400)
 subprocess.run(['docker','compose','restart','app'],cwd=root,check=True,stdout=subprocess.DEVNULL)
 for _ in range(45):
  try:
   with urllib.request.urlopen(base+'/health',timeout=3)as r:
    if r.status==200:break
  except Exception:time.sleep(1)
 else:raise AssertionError('app did not recover')
 rows=a.call('attendance')[1]
 check('Persisted attendance and MySQL session after restart',any(x['id']==aid and x['check_out'] for x in rows))
 with urllib.request.urlopen(base+'/health')as r:headers=dict(r.headers)
 check('Nginx actual security headers',headers.get('X-Frame-Options')=='DENY' and headers.get('X-Content-Type-Options')=='nosniff' and 'Content-Security-Policy'in headers)
 try:urllib.request.urlopen(base+'/demo-missing')
 except urllib.error.HTTPError as x:check('404 log event generated',x.code==404)
 out=root/'docs/evidence';out.mkdir(parents=True,exist_ok=True)
 (out/'integration.json').write_text(json.dumps({'type':'real-system-integration','timestamp':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'tests':results,'headers':headers},ensure_ascii=False,indent=2),encoding='utf-8')
 print(len(results),'integration checks passed')
if __name__=='__main__':main()
