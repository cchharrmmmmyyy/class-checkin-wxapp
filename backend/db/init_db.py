"""
db/init_db.py - 数据库初始化执行入口

功能：
    - 提供 init_database() 函数的直接执行入口
    - 用于命令行直接运行初始化数据库

使用方式：
    python db/init_db.py

注意：
    - 此脚本会重新执行所有建表语句（使用 IF NOT EXISTS，不会删除现有表）
    - 如果启用了测试数据配置，会插入测试数据
    - 只会新增，不会删除或修改现有数据
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import check_and_init_database, init_database

if __name__ == '__main__':
    check_and_init_database()