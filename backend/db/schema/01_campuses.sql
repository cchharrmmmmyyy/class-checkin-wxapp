-- ============================================================
-- 校区表 (campuses)
-- ============================================================
-- 说明：存储学校下辖的校区信息，是组织架构的顶层
--
-- 依赖关系：无
--
-- 字段说明：
--   - id: 自增主键
--   - name: 校区名称，唯一不能重复
--   - address: 校区地址
--   - created_at: 创建时间
--
-- 索引：无特殊索引需求

CREATE TABLE IF NOT EXISTS campuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    address TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);