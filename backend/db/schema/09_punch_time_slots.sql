-- ============================================================
-- 时间段表 (punch_time_slots)
-- ============================================================
-- 说明：存储打卡时间段信息，如早读、上午上课、下午上课等
--
-- 依赖关系：无独立依赖（被 punch_rules 引用）
--
-- 字段说明：
--   - id: 自增主键
--   - name: 时段名称（如 "早读"、"上午上课"）
--   - start_time: 开始时间（HH:MM:SS 格式）
--   - end_time: 结束时间（HH:MM:SS 格式）
--   - enabled: 是否启用（1=启用，0=禁用）
--   - created_at: 创建时间
--   - deleted_at: 软删除时间（为NULL表示未删除）
--
-- 业务规则：
--   - 同一时段可以有多个地理围栏规则
--   - 系统根据当前时间匹配启用的时间段

CREATE TABLE IF NOT EXISTS punch_time_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);