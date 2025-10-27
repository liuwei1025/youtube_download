#!/usr/bin/env python3
"""
数据库配置和连接管理
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncpg
from asyncpg.pool import Pool


class Database:
    """数据库管理类"""
    
    def __init__(self):
        self.pool: Pool = None
        self._connection_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'youtube_tasks'),
            'user': os.getenv('DB_USER', 'youtube'),
            'password': os.getenv('DB_PASSWORD', 'youtube_pass_2024'),
        }
    
    async def connect(self):
        """创建连接池"""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                **self._connection_params,
                min_size=2,
                max_size=10,
                command_timeout=60,
            )
    
    async def disconnect(self):
        """关闭连接池"""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator:
        """获取数据库连接"""
        if self.pool is None:
            await self.connect()
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def execute(self, query: str, *args):
        """执行SQL语句"""
        async with self.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        """查询多行数据"""
        async with self.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """查询单行数据"""
        async with self.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """查询单个值"""
        async with self.acquire() as conn:
            return await conn.fetchval(query, *args)


# 全局数据库实例
db = Database()

