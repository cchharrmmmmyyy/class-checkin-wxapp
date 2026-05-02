-- ============================================================
-- 只读视图集合 (read-only views)
-- ============================================================
-- 说明：
--   - 统一承载 DAO 中重复使用的 users 关联查询
--   - 仅用于读取，不在业务中执行写操作
--   - 通过视图降低重复 JOIN SQL，便于维护字段口径

DROP VIEW IF EXISTS v_leave_user_read;
CREATE VIEW v_leave_user_read AS
SELECT
    l.id,
    l.user_id,
    l.leave_start_date,
    l.leave_end_date,
    l.leave_type,
    l.leave_reason,
    l.leave_status,
    l.approved_by,
    l.approved_at,
    l.created_at,
    l.deleted_at,
    u.username,
    u.class_name
FROM leaves l
JOIN users u ON l.user_id = u.user_id;

DROP VIEW IF EXISTS v_makeup_user_read;
CREATE VIEW v_makeup_user_read AS
SELECT
    mr.id,
    mr.user_id,
    mr.target_date,
    mr.reason,
    mr.status,
    mr.approved_by,
    mr.approved_at,
    mr.created_at,
    mr.deleted_at,
    u.username,
    u.class_name
FROM makeup_requests mr
JOIN users u ON mr.user_id = u.user_id;
