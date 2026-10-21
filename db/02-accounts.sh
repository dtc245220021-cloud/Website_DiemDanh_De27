#!/bin/bash
set -eu
mysql -uroot -p"$MYSQL_ROOT_PASSWORD" <<SQL
REVOKE ALL PRIVILEGES ON attendance.* FROM 'attendance_app'@'%';
GRANT SELECT,INSERT,UPDATE,DELETE ON attendance.* TO 'attendance_app'@'%';
CREATE USER 'exporter'@'%' IDENTIFIED BY '${EXPORTER_PASSWORD}' WITH MAX_USER_CONNECTIONS 3;
GRANT PROCESS,REPLICATION CLIENT,SELECT ON *.* TO 'exporter'@'%';
SQL
