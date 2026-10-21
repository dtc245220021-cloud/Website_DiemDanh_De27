"""Create local secrets once. Never overwrites credentials or an existing database."""
import json,secrets,socket
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def available(start):
 for port in range(start,start+100):
  with socket.socket() as s:
   try: s.bind(('127.0.0.1',port)); return port
   except OSError: pass
 raise RuntimeError('No free localhost port')
def setup():
 if (root/'.env').exists(): raise SystemExit('.env already exists; left unchanged.')
 d={k:secrets.token_hex(24) for k in ['DB_PASSWORD','MYSQL_ROOT_PASSWORD','EXPORTER_PASSWORD','SESSION_SECRET','ADMIN_PASSWORD','EMPLOYEE_PASSWORD','GRAFANA_PASSWORD']}
 d.update({k:str(available(p)) for k,p in [('WEB_PORT',8080),('PMA_PORT',8180),('PROM_PORT',9090),('GRAFANA_PORT',3001),('LOKI_PORT',3100)]})
 (root/'secrets').mkdir(exist_ok=True)
 (root/'secrets/exporter.cnf').write_text('[client]\nuser=exporter\npassword='+d['EXPORTER_PASSWORD']+'\nhost=mysql\n',encoding='utf-8')
 (root/'.env').write_text('\n'.join(f'{k}={v}' for k,v in d.items())+'\n',encoding='utf-8')
 print('Created .env and secrets/exporter.cnf. Passwords stay outside Git. Ports:',json.dumps({k:v for k,v in d.items() if k.endswith('_PORT')}))
if __name__=='__main__': setup()
