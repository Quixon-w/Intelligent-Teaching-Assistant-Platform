#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库使用示例
展示如何使用重构后的知识库功能
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.knowledge import (
    update_knowledge_db, 
    load_vector_db, 
    search_knowledge_db,
    ChromaDBManager,
    BGEM3Manager,
    BGERerankerManager
)
from config.settings import get_settings

def example_teacher_knowledge():
    """教师知识库示例"""
    print("=== 教师知识库示例 ===")
    
    # 1. 更新教师知识库（学习资料）
    print("\n1. 更新教师知识库（学习资料）...")
    chroma_manager = update_knowledge_db(
        userId="teacher001",
        isTeacher=True,
        courseID="CS101",
        lessonNum="lesson1",
        isResource=True,
        isAsk=False
    )
    
    if chroma_manager:
        print("✅ 教师知识库更新成功")
        
        # 2. 加载知识库
        print("\n2. 加载知识库...")
        loaded_manager = load_vector_db(
            userId="teacher001",
            isTeacher=True,
            courseID="CS101",
            lessonNum="lesson1"
        )
        
        if loaded_manager:
            print("✅ 知识库加载成功")
            
            # 3. 搜索知识库
            print("\n3. 搜索知识库...")
            collection_name = "kb_teacher001_CS101_lesson1"
            results = search_knowledge_db(
                query="什么是机器学习？",
                chroma_manager=loaded_manager,
                collection_name=collection_name,
                top_k=3,
                use_rerank=True
            )
            
            print(f"搜索结果数量: {len(results)}")
            for i, result in enumerate(results):
                print(f"\n结果 {i+1}:")
                print(f"文档: {result['document'][:100]}...")
                print(f"分数: {result['score']:.4f}")
                print(f"是否重排序: {result['reranked']}")
    else:
        print("❌ 教师知识库更新失败")

def example_student_knowledge():
    """学生知识库示例"""
    print("\n=== 学生知识库示例 ===")
    
    # 1. 更新学生知识库（可提问文件）
    print("\n1. 更新学生知识库（可提问文件）...")
    chroma_manager = update_knowledge_db(
        userId="student001",
        isTeacher=False,
        courseID=None,
        lessonNum=None,
        isResource=False,
        isAsk=True
    )
    
    if chroma_manager:
        print("✅ 学生知识库更新成功")
        
        # 2. 加载知识库
        print("\n2. 加载知识库...")
        loaded_manager = load_vector_db(
            userId="student001",
            isTeacher=False
        )
        
        if loaded_manager:
            print("✅ 知识库加载成功")
            
            # 3. 搜索知识库
            print("\n3. 搜索知识库...")
            collection_name = "kb_student001_student_default_ask"
            results = search_knowledge_db(
                query="如何学习编程？",
                chroma_manager=loaded_manager,
                collection_name=collection_name,
                top_k=3,
                use_rerank=True
            )
            
            print(f"搜索结果数量: {len(results)}")
            for i, result in enumerate(results):
                print(f"\n结果 {i+1}:")
                print(f"文档: {result['document'][:100]}...")
                print(f"分数: {result['score']:.4f}")
                print(f"是否重排序: {result['reranked']}")
    else:
        print("❌ 学生知识库更新失败")

def example_direct_usage():
    """直接使用模型示例"""
    print("\n=== 直接使用模型示例 ===")
    
    settings = get_settings()
    
    # 1. 使用BGEM3模型
    print("\n1. 使用BGEM3模型...")
    try:
        bgem3_manager = BGEM3Manager(str(settings.BGEM3_MODEL_PATH))
        texts = ["这是一个测试文本", "这是另一个测试文本"]
        embeddings = bgem3_manager.encode(texts)
        print(f"✅ BGEM3编码成功，向量维度: {len(embeddings[0])}")
    except Exception as e:
        print(f"❌ BGEM3编码失败: {e}")
    
    # 2. 使用BGE-Reranker模型
    print("\n2. 使用BGE-Reranker模型...")
    try:
        reranker_manager = BGERerankerManager(str(settings.BGE_RERANKER_MODEL_PATH))
        query = "什么是人工智能？"
        documents = [
            "人工智能是计算机科学的一个分支",
            "机器学习是人工智能的一个重要组成部分",
            "深度学习是机器学习的一个子领域"
        ]
        reranked_results = reranker_manager.rerank_documents(query, documents)
        print("✅ BGE-Reranker重排序成功")
        for score, doc in reranked_results:
            print(f"分数: {score:.4f}, 文档: {doc[:50]}...")
    except Exception as e:
        print(f"❌ BGE-Reranker重排序失败: {e}")
    
    # 3. 使用ChromaDB管理器
    print("\n3. 使用ChromaDB管理器...")
    try:
        chroma_manager = ChromaDBManager(
            host=settings.CHROMADB_HOST,
            port=settings.CHROMADB_PORT
        )
        collections = chroma_manager.list_collections()
        print(f"✅ ChromaDB连接成功，当前collections数量: {len(collections)}")
        for collection in collections:
            print(f"  - {collection.name}")
    except Exception as e:
        print(f"❌ ChromaDB连接失败: {e}")

def main():
    """主函数"""
    print("知识库功能测试")
    print("=" * 50)
    
    # 检查配置
    settings = get_settings()
    print(f"BGEM3模型路径: {settings.BGEM3_MODEL_PATH}")
    print(f"BGE-Reranker模型路径: {settings.BGE_RERANKER_MODEL_PATH}")
    print(f"ChromaDB地址: {settings.CHROMADB_HOST}:{settings.CHROMADB_PORT}")
    
    # 运行示例
    example_direct_usage()
    example_teacher_knowledge()
    example_student_knowledge()
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    main() 