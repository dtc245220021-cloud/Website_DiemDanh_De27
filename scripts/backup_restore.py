"""Dump live DB, restore to a NEW schema, compare content checksums. Keeps live DB intact."""
import subprocess,datetime,json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def sql(query):
 return subprocess.check_output(['docker','compose','exec','-T','mysql','sh','-c','MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot -N -B -e "$1"','sh',query],cwd=root,text=True,encoding='utf-8').strip()
def main():
 stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S');target='attendance_restore_'+stamp
 out=root/'backups';out.mkdir(exist_ok=True)
 dump=subprocess.check_output(['docker','compose','exec','-T','mysql','sh','-c','MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysqldump -uroot --single-transaction --no-tablespaces --set-gtid-purged=OFF attendance'],cwd=root)
 path=out/(target+'.sql');path.write_bytes(dump)
 sql('CREATE DATABASE `'+target+'` CHARACTER SET utf8mb4')
 subprocess.run(['docker','compose','exec','-T','mysql','sh','-c','MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot "$1"','sh',target],cwd=root,input=dump,check=True)
 comparisons=[]
 for table in ['users','shifts','attendance']:
  source=sql(f'CHECKSUM TABLE attendance.{table}').split('\t')[-1];restored=sql(f'CHECKSUM TABLE {target}.{table}').split('\t')[-1]
  assert source==restored and source!='NULL',(table,source,restored)
  comparisons.append({'table':table,'source_checksum':source,'restore_checksum':restored,'match':True})
 result={'restore_schema':target,'backup_file':str(path.relative_to(root)),'backup_bytes':len(dump),'comparisons':comparisons,'note':'Sessions restored but excluded from comparison because requests change session expiry. Restore schema retained for inspection.'}
 evidence=root/'docs/evidence';evidence.mkdir(parents=True,exist_ok=True);(evidence/'backup-restore.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
