'use strict';
const express=require('express'), session=require('express-session'), MySQLStore=require('express-mysql-session')(session);
const mysql=require('mysql2/promise'), bcrypt=require('bcryptjs'), crypto=require('node:crypto'), fs=require('node:fs');
const {rateLimit}=require('express-rate-limit'), validation=require('./validation');
const app=express(); app.disable('x-powered-by'); app.set('trust proxy',1);
const cfg={host:'mysql',user:'attendance_app',password:process.env.DB_PASSWORD,database:'attendance',timezone:'+07:00',dateStrings:true};
const pool=mysql.createPool({...cfg,connectionLimit:10});
function audit(event,data={}){const line=JSON.stringify({timestamp:new Date().toISOString(),event,...data});console.log(line);fs.appendFileSync('/app/logs/app.log',line+'\n');}
app.use(express.json({limit:'16kb'}));
app.use(session({name:'attendance.sid',secret:process.env.SESSION_SECRET,resave:false,saveUninitialized:false,store:new MySQLStore({createDatabaseTable:false,clearExpired:true,...cfg}),cookie:{httpOnly:true,sameSite:'strict',secure:false,maxAge:3600000}}));
app.use(express.static('public',{index:false}));
app.get('/',(req,res)=>res.sendFile(__dirname+'/public/index.html'));
app.get('/health',async(req,res)=>{try{await pool.query('SELECT 1');res.json({status:'ok',database:'connected'});}catch{res.status(503).json({status:'unavailable'});}});
app.get('/api/session',(req,res)=>{req.session.csrf ||=crypto.randomBytes(32).toString('hex');res.json({user:req.session.user||null,csrf:req.session.csrf});});
app.use('/api',(req,res,next)=>{if(!['GET','HEAD'].includes(req.method)&&(!req.session.csrf || req.get('X-CSRF-Token')!==req.session.csrf))return res.status(403).json({error:'Phiên xác thực không hợp lệ. Hãy tải lại trang.'});next();});
const loginLimit=rateLimit({windowMs:15*60000,limit:20,standardHeaders:'draft-8',legacyHeaders:false,message:{error:'Đã thử quá nhiều lần. Vui lòng chờ 15 phút.'}});
app.post('/api/login',loginLimit,async(req,res)=>{
 const {email,password}=req.body;
 if(typeof email!=='string'||typeof password!=='string'||email.length>120||password.length>72)return res.status(400).json({error:'Thông tin đăng nhập không hợp lệ.'});
 const [[u]]=await pool.execute('SELECT * FROM users WHERE email=? AND active=1',[email]);
 if(!u||!await bcrypt.compare(password,u.password_hash)){audit('login_failed');return res.status(401).json({error:'Email hoặc mật khẩu không đúng.'});}
 req.session.regenerate(err=>{if(err)return res.status(500).json({error:'Không tạo được phiên.'});req.session.user={id:u.id,name:u.name,code:u.code,role:u.role};req.session.csrf=crypto.randomBytes(32).toString('hex');req.session.save(err=>{if(err)return res.status(500).json({error:'Không lưu được phiên.'});audit('login_success',{user_id:u.id});res.json({user:req.session.user,csrf:req.session.csrf});});});
});
app.post('/api/logout',(req,res)=>req.session.destroy(()=>{res.clearCookie('attendance.sid');res.json({ok:true});}));
app.use('/api',async(req,res,next)=>{
 if(!req.session.user)return res.status(401).json({error:'Vui lòng đăng nhập.'});
 const [[u]]=await pool.execute('SELECT active,role,name,code FROM users WHERE id=?',[req.session.user.id]);
 if(!u?.active){req.session.destroy(()=>{});return res.status(401).json({error:'Tài khoản đã ngừng hoạt động.'});}
 Object.assign(req.session.user,u);next();
});
const admin=(req,res,next)=>req.session.user.role==='admin'?next():res.status(403).json({error:'Chức năng chỉ dành cho quản trị viên.'});
app.get('/api/shifts',async(req,res)=>res.json((await pool.query('SELECT * FROM shifts ORDER BY start_time'))[0]));
app.get('/api/attendance',async(req,res)=>{
 const params=[],where=[];
 if(req.session.user.role!=='admin'){where.push('a.user_id=?');params.push(req.session.user.id);}
 for(const k of ['from','to'])if(req.query[k]){if(!/^\d{4}-\d{2}-\d{2}$/.test(req.query[k]))return res.status(400).json({error:'Ngày không hợp lệ.'});where.push(`a.work_date ${k==='from'?'>=':'<='} ?`);params.push(req.query[k]);}
 const [rows]=await pool.execute(`SELECT a.*,u.name,u.code,s.name shift_name,s.start_time,s.end_time,ROUND(TIMESTAMPDIFF(MINUTE,a.check_in,a.check_out)/60,2) hours FROM attendance a JOIN users u ON u.id=a.user_id JOIN shifts s ON s.id=a.shift_id ${where.length?'WHERE '+where.join(' AND '):''} ORDER BY a.work_date DESC,a.id DESC LIMIT 500`,params);res.json(rows);
});
app.post('/api/check-in',async(req,res)=>{
 const id=Number(req.body.shift_id);if(!Number.isSafeInteger(id)||id<1)return res.status(400).json({error:'Chọn ca làm hợp lệ.'});
 const con=await pool.getConnection();
 try{await con.beginTransaction();await con.execute('SELECT id FROM users WHERE id=? FOR UPDATE',[req.session.user.id]);
 const [[s]]=await con.execute('SELECT id FROM shifts WHERE id=?',[id]);if(!s){await con.rollback();return res.status(404).json({error:'Ca làm không tồn tại.'});}
 const [[open]]=await con.execute('SELECT id FROM attendance WHERE user_id=? AND check_out IS NULL',[req.session.user.id]);if(open){await con.rollback();return res.status(409).json({error:'Bạn đang trong một ca làm. Hãy ra ca trước.'});}
 await con.execute('INSERT INTO attendance(user_id,shift_id,work_date,check_in) VALUES(?,?,CURDATE(),NOW())',[req.session.user.id,id]);await con.commit();audit('check_in',{user_id:req.session.user.id,shift_id:id});res.status(201).json({ok:true});
 }catch(e){await con.rollback();throw e;}finally{con.release();}
});
app.post('/api/check-out',async(req,res)=>{
 const [r]=await pool.execute('UPDATE attendance SET check_out=NOW() WHERE id=? AND user_id=? AND check_out IS NULL',[Number(req.body.id)||0,req.session.user.id]);
 if(!r.affectedRows)return res.status(409).json({error:'Không tìm thấy ca đang làm của bạn.'});audit('check_out',{user_id:req.session.user.id,attendance_id:Number(req.body.id)});res.json({ok:true});
});
app.get('/api/users',admin,async(req,res)=>res.json((await pool.query('SELECT id,code,name,email,role,active FROM users ORDER BY id'))[0]));
app.post('/api/users',admin,async(req,res)=>{
 const e=validation.person(req.body,true);if(e)return res.status(400).json({error:e});const b=req.body;
 const [r]=await pool.execute('INSERT INTO users(code,name,email,role,password_hash) VALUES(?,?,?,?,?)',[b.code,b.name.trim(),b.email,b.role,await bcrypt.hash(b.password,12)]);audit('user_created',{actor:req.session.user.id,user_id:r.insertId});res.status(201).json({id:r.insertId});
});
app.put('/api/users/:id',admin,async(req,res)=>{
 const e=validation.person(req.body);if(e)return res.status(400).json({error:e});const b=req.body,id=Number(req.params.id)||0;
 if(id===req.session.user.id && (b.role!=='admin'||b.active===false))return res.status(400).json({error:'Không thể tự hạ quyền hoặc vô hiệu hóa tài khoản hiện tại.'});
 const params=[b.code,b.name.trim(),b.email,b.role,b.active!==false];let sql='UPDATE users SET code=?,name=?,email=?,role=?,active=?';if(b.password){sql+=',password_hash=?';params.push(await bcrypt.hash(b.password,12));}params.push(id);
 const [r]=await pool.execute(sql+' WHERE id=?',params);if(!r.affectedRows)return res.status(404).json({error:'Nhân sự không tồn tại.'});audit('user_updated',{actor:req.session.user.id,user_id:id});res.json({ok:true});
});
app.delete('/api/users/:id',admin,async(req,res)=>{
 const id=Number(req.params.id)||0;if(id===req.session.user.id)return res.status(400).json({error:'Không thể vô hiệu hóa chính mình.'});
 const [r]=await pool.execute('UPDATE users SET active=0 WHERE id=?',[id]);if(!r.affectedRows)return res.status(404).json({error:'Nhân sự không tồn tại.'});audit('user_deactivated',{actor:req.session.user.id,user_id:id});res.json({ok:true});
});
app.post('/api/shifts',admin,async(req,res)=>{const e=validation.shift(req.body);if(e)return res.status(400).json({error:e});const b=req.body;const [r]=await pool.execute('INSERT INTO shifts(name,start_time,end_time) VALUES(?,?,?)',[b.name.trim(),b.start_time,b.end_time]);audit('shift_created',{actor:req.session.user.id,shift_id:r.insertId});res.status(201).json({id:r.insertId});});
app.put('/api/shifts/:id',admin,async(req,res)=>{const e=validation.shift(req.body);if(e)return res.status(400).json({error:e});const b=req.body;const [r]=await pool.execute('UPDATE shifts SET name=?,start_time=?,end_time=? WHERE id=?',[b.name.trim(),b.start_time,b.end_time,Number(req.params.id)||0]);if(!r.affectedRows)return res.status(404).json({error:'Ca làm không tồn tại.'});audit('shift_updated',{actor:req.session.user.id});res.json({ok:true});});
app.delete('/api/shifts/:id',admin,async(req,res)=>{const [r]=await pool.execute('DELETE FROM shifts WHERE id=?',[Number(req.params.id)||0]);if(!r.affectedRows)return res.status(404).json({error:'Ca làm không tồn tại.'});audit('shift_deleted',{actor:req.session.user.id});res.json({ok:true});});
app.use((req,res)=>res.status(404).json({error:'Không tìm thấy trang yêu cầu.'}));
app.use((err,req,res,next)=>{
 if(err.code==='ER_DUP_ENTRY')return res.status(409).json({error:'Dữ liệu đã tồn tại. Kiểm tra mã, email, tên ca hoặc lần điểm danh hôm nay.'});
 if(err.code==='ER_ROW_IS_REFERENCED_2')return res.status(409).json({error:'Ca đã có lịch sử điểm danh nên không thể xóa.'});
 if(err.type==='entity.parse.failed')return res.status(400).json({error:'Dữ liệu JSON không hợp lệ.'});
 audit('application_error',{code:err.code||'internal'});res.status(500).json({error:'Hệ thống gặp lỗi. Vui lòng thử lại.'});
});
async function seed(){
 const [[{n}]]=await pool.query('SELECT COUNT(*) n FROM users');if(n)return;
 await pool.query("INSERT INTO shifts(name,start_time,end_time) VALUES ('Ca sáng','08:00','12:00'),('Ca chiều','13:00','17:00'),('Ca hành chính','08:00','17:00')");
 const hash=await bcrypt.hash(process.env.EMPLOYEE_PASSWORD,12);
 await pool.execute('INSERT INTO users(code,name,email,password_hash,role) VALUES(?,?,?,?,?)',['QT01','Chu Thế Mạnh','admin@attendance.local',await bcrypt.hash(process.env.ADMIN_PASSWORD,12),'admin']);
 for(const [i,name]of ['Nguyễn Minh Anh','Trần Hoàng Nam','Lê Thu Hà','Phạm Đức Huy','Vũ Ngọc Linh'].entries())await pool.execute('INSERT INTO users(code,name,email,password_hash) VALUES(?,?,?,?)',[`NV0${i+1}`,name,`nv0${i+1}@attendance.local`,hash]);
 await pool.query("INSERT INTO attendance(user_id,shift_id,work_date,check_in,check_out) SELECT id,1,CURDATE()-INTERVAL 1 DAY,CONCAT(CURDATE()-INTERVAL 1 DAY,' 08:00:00'),CONCAT(CURDATE()-INTERVAL 1 DAY,' 12:00:00') FROM users WHERE role='employee'");audit('seed_completed',{demo_data:true});
}
seed().then(()=>app.listen(3000,'0.0.0.0',()=>audit('server_started'))).catch(e=>{console.error(e.code||'startup_failed');process.exit(1);});
