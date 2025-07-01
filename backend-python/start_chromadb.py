#!/usr/bin/env python3
"""
ChromaDB服务器启动脚本
"""

import subprocess
import time
import os
import sys
from config.settings import get_settings

def start_chromadb_server():
    """启动ChromaDB服务器"""
    settings = get_settings()
    
    print(f"🚀 正在启动ChromaDB服务器...")
    print(f"   主机: {settings.CHROMADB_HOST}")
    print(f"   端口: {settings.CHROMADB_PORT}")
    
    try:
        # 启动ChromaDB服务器
        cmd = [
            "chroma", "run", 
            "--host", settings.CHROMADB_HOST,
            "--port", str(settings.CHROMADB_PORT),
            "--path", "/tmp/chromadb"  # 数据存储路径
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        # 启动ChromaDB服务器
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务器启动
        time.sleep(3)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("✅ ChromaDB服务器启动成功！")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ ChromaDB服务器启动失败:")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ 启动ChromaDB服务器时出错: {e}")
        return None

def check_chromadb_connection():
    """检查ChromaDB连接"""
    settings = get_settings()
    
    try:
        import chromadb
        client = chromadb.HttpClient(
            host=settings.CHROMADB_HOST,
            port=settings.CHROMADB_PORT
        )
        collections = client.list_collections()
        print(f"✅ ChromaDB连接成功！当前collections数量: {len(collections)}")
        return True
    except Exception as e:
        print(f"❌ ChromaDB连接失败: {e}")
        return False

if __name__ == "__main__":
    # 启动ChromaDB服务器
    process = start_chromadb_server()
    
    if process:
        # 等待一段时间后检查连接
        time.sleep(2)
        check_chromadb_connection()
        
        try:
            # 保持服务器运行
            print("ChromaDB服务器正在运行... (按Ctrl+C停止)")
            process.wait()
        except KeyboardInterrupt:
            print("\n正在停止ChromaDB服务器...")
            process.terminate()
            process.wait()
            print("ChromaDB服务器已停止")
    else:
        print("无法启动ChromaDB服务器")
        sys.exit(1) 