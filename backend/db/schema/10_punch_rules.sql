-- ============================================================
-- 打卡规则表 (punch_rules)
-- ============================================================
-- 说明：存储打卡规则，关联时间段和地理围栏，支持优先级配置
--
-- 依赖关系：punch_time_slots (time_slot_id), punch_geofences (geofence_id)
--
-- 字段说明：
--   - id: 自增主键
--   - time_slot_id: 时间段ID
--   - geofence_id: 地理围栏ID
--   - priority: 优先级（数字越小优先级越高）
--   - time_enabled: 是否启用时间校验（1=启用，0=禁用）
--   - location_enabled: 是否启用位置校验（1=启用，0=禁用）
--   - enabled: 规则是否启用（1=启用，0=禁用）
--   - created_at: 创建时间
--   - deleted_at: 软删除时间（为NULL表示未删除）
--
-- 业务规则：
--   - 打卡时，系统匹配当前时间段和位置的规则
--   - 按 priority 升序取第一条匹配的规则
--   - 如果 time_enabled=0，则不检查打卡时间是否在时间段内
--   - 如果 location_enabled=0，则不检查打卡位置是否在围栏内
--
-- 外键：
--   - time_slot_id -> punch_time_slots(id) ON DELETE CASCADE
--   - geofence_id -> punch_geofences(id) ON DELETE CASCADE

CREATE TABLE IF NOT EXISTS punch_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time_slot_id INTEGER NOT NULL,
    geofence_id INTEGER NOT NULL,
    priority INTEGER NOT NULL DEFAULT 100,
    time_enabled INTEGER NOT NULL DEFAULT 1,
    location_enabled INTEGER NOT NULL DEFAULT 1,
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    FOREIGN KEY (time_slot_id) REFERENCES punch_time_slots(id) ON DELETE CASCADE,
    FOREIGN KEY (geofence_id) REFERENCES punch_geofences(id) ON DELETE CASCADE
);