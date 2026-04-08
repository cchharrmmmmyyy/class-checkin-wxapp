-- ============================================================
-- 班级表 (classes)
-- ============================================================
-- 说明：存储班级信息，隶属于年级
--
-- 依赖关系：grades (grade_id)
--
-- 字段说明：
--   - class_name: 班级名称作为主键（如 "计算机2401"）
--   - grade_id: 所属年级的外键
--   - created_at: 创建时间
--   - deleted_at: 软删除时间（为NULL表示未删除）
--
-- 软删除：删除操作只设置 deleted_at，不物理删除
-- 外键：grade_id -> grades(id) ON DELETE CASCADE

CREATE TABLE IF NOT EXISTS classes (
    class_name TEXT PRIMARY KEY,
    grade_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    FOREIGN KEY (grade_id) REFERENCES grades(id) ON DELETE CASCADE
);