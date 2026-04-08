-- ============================================================
-- 用户表 (users)
-- ============================================================
-- 说明：存储所有用户信息，包括学生、教师、班委、管理员
--
-- 依赖关系：classes (class_name)
--
-- 字段说明：
--   - user_id: 用户ID（学号/工号），作为主键
--   - username: 登录账号，唯一
--   - password: 密码哈希（使用 bcrypt/argon2）
--   - real_name: 真实姓名
--   - role: 角色，可选值：admin-管理员，teacher-教师，monitor-班委，student-学生
--   - class_name: 所属班级（学生/班委必填，教师/管理员可为NULL）
--   - student_id: 学号（学生/班委专用，唯一）
--   - phone: 联系电话
--   - email: 邮箱
--   - is_first_login: 是否首次登录（1=是，0=否），首次登录需修改密码
--   - last_punch_time: 最后一次打卡时间（用于防止频繁打卡）
--   - login_fail_count: 连续登录失败次数，达到3次将锁定账号
--   - lock_until: 账号锁定截止时间
--   - last_login_time: 最后登录时间
--   - last_login_ip: 最后登录IP（支持IPv6）
--   - created_at: 创建时间
--   - deleted_at: 软删除时间（为NULL表示未删除）
--
-- 角色权限说明：
--   - admin: 管理员，全权限，可管理所有数据
--   - teacher: 教师，可管理自己任教班级的学生考勤
--   - monitor: 班委，可查看本班打卡记录，无审批权
--   - student: 学生，可打卡、请假、申请补卡
--
-- 外键：class_name -> classes(class_name) ON DELETE SET NULL
-- 软删除：删除操作只设置 deleted_at

CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    real_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin','teacher','monitor','student')),
    class_name TEXT,
    student_id TEXT UNIQUE,
    phone TEXT,
    email TEXT,
    is_first_login INTEGER NOT NULL DEFAULT 1,
    last_punch_time TIMESTAMP,
    login_fail_count INTEGER NOT NULL DEFAULT 0,
    lock_until TIMESTAMP,
    last_login_time TIMESTAMP,
    last_login_ip TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    FOREIGN KEY (class_name) REFERENCES classes(class_name) ON DELETE SET NULL
);

-- indexes for users
CREATE INDEX IF NOT EXISTS idx_users_student_id ON users(student_id);  -- 学号查询
CREATE INDEX IF NOT EXISTS idx_users_class_name ON users(class_name) WHERE deleted_at IS NULL;  -- 班级查学生
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);  -- 角色筛选