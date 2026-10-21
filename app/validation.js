'use strict';
function person(body, creating = false) {
  const {code,name,email,role,password} = body;
  if (!/^[A-Za-z0-9_-]{2,30}$/.test(code||'') || !name?.trim() || name.length>100 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email||'') || email.length>120 || !['admin','employee'].includes(role)) return 'Thông tin nhân sự không hợp lệ. Kiểm tra mã, họ tên, email và vai trò.';
  if ((creating || password) && (typeof password !== 'string' || password.length<12 || password.length>72)) return 'Mật khẩu phải có từ 12 đến 72 ký tự.';
  return null;
}
function shift(body) {
  const {name,start_time,end_time}=body;
  if (!name?.trim() || name.length>80 || !/^\d{2}:\d{2}$/.test(start_time||'') || !/^\d{2}:\d{2}$/.test(end_time||'') || start_time>='24:00' || end_time>='24:00' || +start_time.slice(3)>59 || +end_time.slice(3)>59 || end_time<=start_time) return 'Ca làm phải có tên và giờ hợp lệ; giờ kết thúc sau giờ bắt đầu trong cùng ngày.';
  return null;
}
module.exports={person,shift};
