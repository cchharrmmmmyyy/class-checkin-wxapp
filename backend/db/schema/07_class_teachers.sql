-- ============================================================
-- 教师任课表 (class_teachers)
-- ============================================================
-- 说明：存储教师与班级的任课关系，支持多教师任同一班级
--
-- 依赖关系：classes (class_name), users (teacher_id)
--
-- 字段说明：
--   - class_name: 班级名称（复合主键）
--   - teacher_id: 教师ID（复合主键，引用 users.user_id）
--   - semester: 任教学期（如 "2024-2025-1" 表示2024-2025学年第一学期）
--   - created_at: 创建时间
--   - deleted_at: 软删除时间（为NULL表示未删除，撤销任课）
--
-- 复合主键：(class_name, teacher_id)
-- 外键：
--   - class_name -> classes(class_name) ON DELETE CASCADE
--   - teacher_id -> users(user_id) ON DELETE CASCADE

CREATE TABLE IF NOT EXISTS class_teachers (
    class_name TEXT NOT NULL,
    teacher_id TEXT NOT NULL,
    semester TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    PRIMARY KEY (class_name, teacher_id),
    FOREIGN KEY (class_name) REFERENCES classes(class_name) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES users(user_id) ON DELETE CASCADE
);