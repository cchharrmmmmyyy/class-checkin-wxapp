-- ============================================================
-- 补卡申请表 (makeup_requests)
-- ============================================================
-- 说明：存储学生的补卡申请记录
--
-- 依赖关系：users (user_id, approved_by)
--
-- 字段说明：
--   - id: 自增主键
--   - user_id: 申请人ID（学生）
--   - target_date: 需要补卡的日期
--   - reason: 补卡理由
--   - status: 审批状态，pending-待审批，approved-已批准，rejected-已拒绝
--   - approved_by: 审批人ID（教师/管理员）
--   - approved_at: 审批时间
--   - created_at: 申请时间
--   - deleted_at: 软删除时间（为NULL表示未删除）
--
-- 业务规则：
--   - 补卡申请审批通过后，系统自动生成打卡记录
--   - 只有 punch_config.allow_makeup=1 时才允许申请补卡
--   - 审批后自动生成通知发送给申请人
--
-- 外键：
--   - user_id -> users(user_id) ON DELETE CASCADE
--   - approved_by -> users(user_id) ON DELETE SET NULL
--
-- 索引说明：
--   - idx_makeup_user_status: 按用户和状态查询申请记录

CREATE TABLE IF NOT EXISTS makeup_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    target_date DATE NOT NULL,
    reason TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
    approved_by TEXT,
    approved_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(user_id) ON DELETE SET NULL
);

-- indexes for makeup_requests
CREATE INDEX IF NOT EXISTS idx_makeup_user_status ON makeup_requests(user_id, status);