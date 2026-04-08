-- ============================================================
-- 年级表 (grades)
-- ============================================================
-- 说明：存储年级信息，隶属于专业
--
-- 依赖关系：majors (major_id)
--
-- 字段说明：
--   - id: 自增主键
--   - major_id: 所属专业的外键
--   - year: 入学年份（如 2024）
--   - name: 年级名称（如 "2024级"）
--   - created_at: 创建时间
--
-- 唯一约束：(major_id, year) - 同一专业下年份不能重复
-- 外键：major_id -> majors(id) ON DELETE CASCADE

CREATE TABLE IF NOT EXISTS grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    major_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (major_id) REFERENCES majors(id) ON DELETE CASCADE,
    UNIQUE(major_id, year)
);