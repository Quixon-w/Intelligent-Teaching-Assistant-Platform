#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Domain知识库构建脚本

使用方法：
1. 将教学相关的文档文件（.txt, .md, .pdf, .docx）放入 base-knowledge/domain_knowledge/domain_docs/ 目录
2. 运行此脚本：python scripts/build_domain_knowledge.py

脚本会自动：
1. 扫描domain_docs目录中的所有文档
2. 将文档分块并向量化
3. 存储到ChromaDB的domain_knowledge collection中
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.knowledge import build_domain_knowledge, ensure_domain_knowledge_exists
from config.settings import get_settings


def main():
    """主函数"""
    print("🚀 开始构建Domain知识库...")
    print("=" * 50)
    
    try:
        # 获取配置
        settings = get_settings()
        
        # 检查domain_docs目录
        domain_docs_dir = settings.DOMAIN_DOCS_DIR
        print(f"📁 Domain文档目录: {domain_docs_dir}")
        
        if not domain_docs_dir.exists():
            print(f"❌ Domain文档目录不存在，正在创建: {domain_docs_dir}")
            domain_docs_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ 目录创建成功")
            print(f"💡 请将教学相关的文档文件放入此目录，然后重新运行脚本")
            return
        
        # 检查是否有文档文件
        doc_files = []
        for file_path in domain_docs_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.txt', '.md', '.pdf', '.docx']:
                doc_files.append(file_path)
        
        if not doc_files:
            print("❌ 没有找到支持的文档文件")
            print(f"💡 请将以下类型的文件放入 {domain_docs_dir}:")
            print("   - .txt (文本文件)")
            print("   - .md (Markdown文件)")
            print("   - .pdf (PDF文件)")
            print("   - .docx (Word文档)")
            return
        
        print(f"📄 找到 {len(doc_files)} 个文档文件:")
        for file_path in doc_files:
            print(f"   - {file_path.name}")
        
        print("\n" + "=" * 50)
        
        # 检查是否已存在知识库
        print("🔍 检查现有知识库...")
        if ensure_domain_knowledge_exists():
            print("✅ Domain知识库已存在且有效")
            
            # 询问是否重新构建
            response = input("\n是否要重新构建知识库？(y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("✅ 保持现有知识库不变")
                return
        
        # 构建知识库
        print("\n🔧 开始构建Domain知识库...")
        success = build_domain_knowledge()
        
        if success:
            print("\n" + "=" * 50)
            print("🎉 Domain知识库构建成功！")
            print("✅ 现在可以在问答和大纲生成中使用domain知识库了")
        else:
            print("\n" + "=" * 50)
            print("❌ Domain知识库构建失败")
            print("💡 请检查文档文件格式和ChromaDB服务状态")
            
    except Exception as e:
        print(f"\n❌ 构建过程中出错: {e}")
        print("💡 请检查配置文件和依赖项")


if __name__ == "__main__":
    main() 