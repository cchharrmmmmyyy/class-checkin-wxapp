# 后端问题清单

## 已修复 (本次)

| # | 问题 | 状态 |
|----|------|------|
| 1 | log_service.py:37 — 变量名错误，AttributeError | ✅ 已修复 — `operation_log_dao` → `operation_log_dao_instance` |
| 2 | notification_service.py:106 — 未读计数返回错误值 | ✅ 已修复 — `len(notifications)` → `notifications.get('total', 0)` |
| 3 | admin_attendance_service.py:41-44 — IN 子句不通过 SAFE_WHERE_PATTERN | ✅ 已修复 — `base_dao.py` SAFE_WHERE_PATTERN 增加 `IN` 支持 |
| 4 | statistics_service.py:204-211 — 同样的 IN 子句问题 | ✅ 已修复（同上） |
| 5 | notification_service.py:128 — mark_all_as_read 遍历错误 | ✅ 已修复 — `for n in notifications:` → `for n in notifications.get('items', []):` |
| 6 | dao/leave_dao.py 和 dao/makeup_request_dao.py — count() 绕过 SQL 注入防护 | ✅ 已修复 — 两处 count() 均增加 SAFE_WHERE_PATTERN 校验 |
| 7 | services/monitor_service.py — 死代码 | ✅ 已删除 |
| 8 | utils/password.py:11 — bare except | ✅ 已修复 — `except:` → `except Exception:` |

---

## 低优先级

### 9. 文件行数超标

项目规则要求文件 ≤300 行，以下文件超出：

| 文件 | 行数 |
|------|------|
| `services/admin_org_service.py` | 311 |
| `services/statistics_service.py` | 302 |

---

## 已修复 (之前)

| # | 问题 | 状态 |
|----|------|------|
| ~1~ | statistics_service.py/leave_service.py WHERE 字符串字面量 (`= 'approved'`) | ✅ 已修复 |
| ~2~ | routes/student.py + routes/teacher.py 方法名拼写错误 (`get_pending_applications`) | ✅ 已修复 |
