-- ============================================================
-- 全局配置表 (punch_config)
-- ============================================================
-- 说明：存储考勤系统的全局配置信息，该表只有一行
--
-- 依赖关系：无
--
-- 字段说明：
--   - id: 主键，固定为 1
--   - global_time_check_enabled: 全局时间校验开关（1=开，0=关）
--   - global_location_check_enabled: 全局位置校验开关（1=开，0=关）
--   - allow_multi_punch: 是否允许多人同设备打卡（1=允许，0=禁止）
--   - allow_makeup: 是否允许补卡申请（1=允许，0=禁止）
--   - holiday_ranges: 放假日期段，JSON格式
--     示例：[{"start":"2025-07-01","end":"2025-08-31"},{"start":"2025-10-01","end":"2025-10-07"}]
--   - updated_at: 最后更新时间
--
-- 业务规则：
--   - 该表只有一行，id 固定为 1
--   - global_time_check_enabled=0 时，所有规则的时间校验被跳过
--   - global_location_check_enabled=0 时，所有规则的位置校验被跳过
--   - allow_multi_punch=0 时，系统会检测 device_id 重复情况
--   - holiday_ranges 用于排除节假日，不计入应打卡天数

CREATE TABLE IF NOT EXISTS punch_config (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    global_time_check_enabled INTEGER NOT NULL DEFAULT 1,
    global_location_check_enabled INTEGER NOT NULL DEFAULT 1,
    allow_multi_punch INTEGER NOT NULL DEFAULT 0,
    allow_makeup INTEGER NOT NULL DEFAULT 1,
    holiday_ranges TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);