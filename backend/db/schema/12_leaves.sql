-- ============================================================
-- 请假申请表 (leaves)
-- ============================================================
-- 说明：存储学生的请假申请记录
--
-- 依赖关系：users (user_id, approved_by)
--
-- 字段说明：
--   - id: 自增主键
--   - user_id: 申请人ID（学生）
--   - leave_start_date: 请假开始日期
--   - leave_end_date: 请假结束日期
--   - leave_type: 请假类型（病假/事假/公假等）
--   - leave_reason: 请假理由
--   - leave_status: 审批状态，pending-待审批，approved-已批准，rejected-已拒绝
--   - approved_by: 审批人ID（教师/管理员）
--   - approved_at: 审批时间
--   - created_at: 申请时间
--   - deleted_at: 软删除时间（为NULL表示未删除）
--
-- 业务规则：
--   - 请假审批通过后，在请假日期范围内的打卡应被系统忽略
--   - 只有 pending 状态的请假单可以被审批
--   - 审批后自动生成通知发送给申请人
--
-- 外键：
--   - user_id -> users(user_id) ON DELETE CASCADE
--   - approved_by -> users(user_id) ON DELETE SET NULL
--
-- 索引说明：
--   - idx_leaves_user: 按申请人查询
--   - idx_leaves_status: 按状态查询待审批列表
--   - idx_leaves_dates: 按日期范围查询

CREATE TABLE IF NOT EXISTS leaves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    leave_start_date DATE NOT NULL,
    leave_end_date DATE NOT NULL,
    leave_type TEXT NOT NULL,
    leave_reason TEXT,
    leave_status TEXT NOT NULL DEFAULT 'pending' CHECK(leave_status IN ('pending','approved','rejected')),
    approved_by TEXT,
    approved_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(user_id) ON DELETE SET NULL
);

-- indexes for leaves
CREATE INDEX IF NOT EXISTS idx_leaves_user ON leaves(user_id);
CREATE INDEX IF NOT EXISTS idx_leaves_status ON leaves(leave_status) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_leaves_dates ON leaves(leave_start_date, leave_end_date);