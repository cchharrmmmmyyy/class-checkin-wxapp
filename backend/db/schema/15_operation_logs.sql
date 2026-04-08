-- ============================================================
-- 操作日志表 (operation_logs)
-- ============================================================
-- 说明：存储关键业务操作的审计日志，用于安全审计
--
-- 依赖关系：users (operator_id)
--
-- 字段说明：
--   - id: 自增主键
--   - operator_id: 操作人ID
--   - operation_type: 操作类型（如 update_punch, approve_leave 等）
--   - target_type: 目标对象类型（如 punches, leaves, users 等）
--   - target_id: 目标对象的主键值
--   - before_data: 修改前的数据（JSON格式）
--   - after_data: 修改后的数据（JSON格式）
--   - ip_address: 操作者IP地址
--   - created_at: 操作时间
--
-- 需要记录日志的操作：
--   - punches: 更新、删除
--   - leaves: 创建、审批、删除
--   - makeup_requests: 创建、审批、删除
--   - users: 创建、更新、删除（管理员操作）
--   - punch_config: 更新
--
-- 外键：operator_id -> users(user_id) ON DELETE CASCADE
--
-- 索引说明：
--   - idx_logs_operator: 按操作人查询审计记录
--   - idx_logs_target: 按目标对象查询审计记录

CREATE TABLE IF NOT EXISTS operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operator_id TEXT NOT NULL,
    operation_type TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    before_data TEXT,
    after_data TEXT,
    ip_address TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operator_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- indexes for operation_logs
CREATE INDEX IF NOT EXISTS idx_logs_operator ON operation_logs(operator_id);
CREATE INDEX IF NOT EXISTS idx_logs_target ON operation_logs(target_type, target_id);