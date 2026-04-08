-- ============================================================
-- 学院表 (departments)
-- ============================================================
-- 说明：存储学院/系部信息，隶属于校区
--
-- 依赖关系：campuses (campus_id)
--
-- 字段说明：
--   - id: 自增主键
--   - campus_id: 所属校区的外键
--   - name: 学院名称，唯一不能重复
--   - code: 学院代码（如 "CS" 表示计算机学院）
--   - created_at: 创建时间
--
-- 外键：campus_id -> campuses(id) ON DELETE CASCADE

CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campus_id INTEGER NOT NULL,
    name TEXT NOT NULL UNIQUE,
    code TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campus_id) REFERENCES campuses(id) ON DELETE CASCADE
);