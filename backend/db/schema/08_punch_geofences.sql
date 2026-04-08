-- ============================================================
-- 地理围栏表 (punch_geofences)
-- ============================================================
-- 说明：存储打卡地点的地理围栏信息，支持圆形和多边形两种类型
--
-- 依赖关系：无独立依赖（被 punch_rules 引用）
--
-- 字段说明：
--   - id: 自增主键
--   - name: 围栏名称（如 "教学楼A"、"图书馆"）
--   - fence_type: 围栏类型，circle-圆形，polygon-多边形
--   - latitude: 圆心纬度（circle 类型使用）
--   - longitude: 圆心经度（circle 类型使用）
--   - radius: 半径/米（circle 类型使用）
--   - polygon_coords: 多边形顶点坐标（polygon 类型使用），JSON格式
--   - enabled: 是否启用（1=启用，0=禁用）
--   - created_at: 创建时间
--   - deleted_at: 软删除时间（为NULL表示未删除）
--
-- 围栏类型说明：
--   - circle: 圆形围栏，使用 (latitude, longitude, radius) 定义
--   - polygon: 多边形围栏，使用 polygon_coords 定义顶点坐标

CREATE TABLE IF NOT EXISTS punch_geofences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    fence_type TEXT NOT NULL CHECK(fence_type IN ('circle','polygon')),
    latitude REAL,
    longitude REAL,
    radius INTEGER,
    polygon_coords TEXT,
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);