-- ============================================================
-- 专业表 (majors)
-- ============================================================
-- 说明：存储专业信息，隶属于学院
--
-- 依赖关系：departments (department_id)
--
-- 字段说明：
--   - id: 自增主键
--   - department_id: 所属学院的外键
--   - name: 专业名称，唯一不能重复
--   - code: 专业代码（如 "CS001"）
--   - created_at: 创建时间
--
-- 外键：department_id -> departments(id) ON DELETE CASCADE

CREATE TABLE IF NOT EXISTS majors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER NOT NULL,
    name TEXT NOT NULL UNIQUE,
    code TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
);