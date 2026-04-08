-- ============================================================
-- 通知表 (notifications)
-- ============================================================
-- 说明：存储系统内部通知消息，如审批结果通知等
--
-- 依赖关系：users (receiver_id, sender_id)
--
-- 字段说明：
--   - id: 自增主键
--   - receiver_id: 接收人ID（必填）
--   - sender_id: 发送人ID（可为NULL，表示系统通知）
--   - title: 通知标题
--   - content: 通知内容
--   - type: 通知类型（如 leave_approved, leave_rejected, makeup_approved 等）
--   - is_read: 是否已读（1=已读，0=未读）
--   - related_id: 关联业务ID（如请假单ID），用于跳转查看详情
--   - created_at: 创建时间
--
-- 通知类型说明：
--   - leave_approved: 请假已批准
--   - leave_rejected: 请假已拒绝
--   - makeup_approved: 补卡已批准
--   - makeup_rejected: 补卡已拒绝
--   - punch_reminder: 打卡提醒（可选功能）
--
-- 外键：
--   - receiver_id -> users(user_id) ON DELETE CASCADE
--   - sender_id -> users(user_id) ON DELETE SET NULL（发送人删除时通知保留）
--
-- 索引说明：
--   - idx_notifications_receiver: 按接收人查询未读消息

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receiver_id TEXT NOT NULL,
    sender_id TEXT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    type TEXT NOT NULL,
    is_read INTEGER NOT NULL DEFAULT 0,
    related_id TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (receiver_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- indexes for notifications
CREATE INDEX IF NOT EXISTS idx_notifications_receiver ON notifications(receiver_id, is_read);