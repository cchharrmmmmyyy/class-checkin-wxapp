-- ============================================================
-- 打卡记录表 (punches)
-- ============================================================
-- 说明：存储学生的打卡记录
--
-- 依赖关系：users (user_id), punch_rules (matched_rule_id)
--
-- 字段说明：
--   - id: 自增主键
--   - user_id: 用户ID（学生）
--   - punch_date: 打卡日期
--   - punch_time: 打卡时间
--   - latitude: 打卡时纬度
--   - longitude: 打卡时经度
--   - matched_rule_id: 匹配到的规则ID（用于审计）
--   - is_makeup: 是否为补卡记录（1=是，0=否）
--   - device_id: 设备唯一标识（用于防作弊检测）
--   - created_at: 创建时间
--
-- 业务规则：
--   - 同一用户同一天可以有多条打卡记录（如果 allow_multi_punch=1）
--   - 系统通过 device_id 检测多人同设备打卡（防作弊）
--   - matched_rule_id 用于记录匹配了哪条规则，便于审计
--
-- 外键：
--   - user_id -> users(user_id) ON DELETE CASCADE
--   - matched_rule_id -> punch_rules(id) ON DELETE SET NULL
--
-- 索引说明：
--   - idx_punches_user_date: 按用户和日期查询
--   - idx_punches_device_date: 按设备ID和日期查询（防作弊）

CREATE TABLE IF NOT EXISTS punches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    punch_date DATE NOT NULL,
    punch_time TIME NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    matched_rule_id INTEGER,
    is_makeup INTEGER NOT NULL DEFAULT 0,
    device_id TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (matched_rule_id) REFERENCES punch_rules(id) ON DELETE SET NULL
);

-- indexes for punches
CREATE INDEX IF NOT EXISTS idx_punches_user_date ON punches(user_id, punch_date);
CREATE INDEX IF NOT EXISTS idx_punches_device_date ON punches(device_id, punch_date);