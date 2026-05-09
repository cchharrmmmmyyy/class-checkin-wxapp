# Services 层重构计划 — P0 先行 + TDD

> 审查日期：2026-05-09
> 状态：待执行

---

## 策略

采用 **TDD（测试驱动开发）** 方式：**先编写测试代码，确认测试失败 → 再重构/实现代码 → 确认测试通过**。

---

## 第一阶段：P0 重构（3 项）

### P0-A：新建 `utils/pagination.py` — 唯一分页工具

**TDD 步骤：**

1. **写测试** → `tests/test_utils_pagination.py`
   - 测试 `paginate(items, total, page, size)` 正常场景
   - 测试 `paginate()` 当 `size=None`（不分页）
   - 测试 `paginate()` 当 `items=[]`
   - 测试 `normalize_pagination()` 正常参数
   - 测试 `normalize_pagination()` 非法参数（page<1, size<1）
   - 测试 `normalize_pagination()` 当 `size=None`

2. **实现** → `utils/pagination.py`
   - `paginate(items, total, page, size)` → 构建统一分页响应
   - `normalize_pagination(page, size)` → 校验并标准化分页参数

3. **替换** → 7 个 Service 文件中的重复分页代码

---

### P0-B：增强 `utils/error_codes.py` — 完整错误码常量

**TDD 步骤：**

1. **写测试** → `tests/test_error_codes.py`
   - 测试所有常量存在且值唯一
   - 测试常量值在正确的码段范围内

2. **实现** → 补充 `utils/error_codes.py` 全部缺失常量

3. **替换** → 全部 11 个 Service 文件的魔法数字 → error_codes 常量

---

### P0-C：拆分 `admin_service.py`（1141 行 → 5 个子 Service）

**TDD 步骤：**

1. **写测试** → `tests/test_admin_services/` 目录，每个子 Service 对应一个测试文件
   - 先测试原始 `AdminService` 各方法的**行为**（接口契约）
   - 测试依赖：使用 `conftest.py` 的 in-memory SQLite + 种子数据

2. **创建子 Service**：
   - `services/admin_org_service.py` → `AdminOrgService`
   - `services/admin_user_service.py` → `AdminUserService`
   - `services/admin_rule_service.py` → `AdminRuleService`
   - `services/admin_teaching_service.py` → `AdminTeachingService`
   - `services/admin_attendance_service.py` → `AdminAttendanceService`

3. **替换引用**：
   - 更新 `services/__init__.py`
   - 更新路由层的 import（`routes/admin/*.py`）

4. **验证**：测试对新子 Service 的调用结果 = 与原始 Service 行为一致

---

## 测试基础设施

### `tests/conftest.py`

```python
# 1. 设置测试环境变量（覆盖 config.Config）
# 2. 使用 in-memory SQLite 数据库
# 3. 执行所有 schema SQL 建表
# 4. 提供 fixture:
#    - app: Flask 测试 app
#    - db: 数据库连接
#    - seed_data: 基础种子数据（校区/院系/专业/年级/班级/用户等）
```

### 目录结构

```
tests/
├── conftest.py              # 测试配置与 fixtures
├── test_utils_pagination.py  # P0-A: 分页工具测试
├── test_error_codes.py       # P0-B: 错误码常量测试
└── test_admin_services/      # P0-C: admin_service 拆分测试
    ├── __init__.py
    ├── test_admin_org.py
    ├── test_admin_user.py
    ├── test_admin_rule.py
    ├── test_admin_teaching.py
    └── test_admin_attendance.py
```

---

## 执行顺序（分步实施）

```
Step 1 — 测试基础设施
  └── 创建 tests/conftest.py（in-memory SQLite + fixtures）

Step 2 — P0-A: 分页工具 (TDD)
  ├── 写测试 tests/test_utils_pagination.py
  ├── 实现 utils/pagination.py
  └── 验证测试通过

Step 3 — P0-B: 错误码常量 (TDD)
  ├── 写测试 tests/test_error_codes.py
  ├── 增强 utils/error_codes.py
  └── 验证测试通过

Step 4 — P0-C: 写 admin_service 行为测试 (TDD)
  ├── tests/test_admin_services/test_admin_org.py
  ├── tests/test_admin_services/test_admin_user.py
  ├── tests/test_admin_services/test_admin_rule.py
  ├── tests/test_admin_services/test_admin_teaching.py
  ├── tests/test_admin_services/test_admin_attendance.py
  └── 运行测试（应全部通过，验证当前行为）

Step 5 — 创建 utils/serializers.py（拆分的依赖）
  └── 抽取 _to_time_str / _as_bool_int / _serialize_* 等工具函数

Step 6 — 拆分 admin_service.py
  ├── 创建 5 个子 Service 文件
  ├── 精简原 admin_service.py（仅保留向后兼容导入）
  └── 更新 services/__init__.py

Step 7 — 替换路由层引用
  ├── 更新 routes/admin/*.py 导入子 Service
  └── 运行测试验证行为一致

Step 8 — 替换 Service 层的分页代码
  ├── punch_service.py → paginate()
  ├── leave_service.py → paginate()
  ├── makeup_service.py → paginate()
  ├── teacher_service.py → paginate()
  ├── notification_service.py → paginate()
  ├── log_service.py → paginate()
  └── 子 Service → paginate()

Step 9 — 替换 Service 层的错误码
  ├── 全部 11 个 Service 文件替换魔法数字
  └── 验证测试通过
```

---

## 验收标准

1. `utils/pagination.py` 测试覆盖率 100%
2. `utils/error_codes.py` 包含所有业务领域错误码常量
3. `admin_service.py` 拆分后每个子 Service ≤ 300 行
4. 所有分页响应使用 `paginate()` 构建
5. 所有 `ServiceException` 使用 `error_codes.py` 常量
6. 原 `services/__init__.py` 的导出接口向后兼容
7. 路由层 import 正确指向新的子 Service
