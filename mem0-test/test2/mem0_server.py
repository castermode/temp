"""
Mem0 HTTP 服务器
提供记忆管理的 REST API 服务

运行方式:
    python mem0_server.py

访问 API 文档:
    http://localhost:8000/docs

环境变量要求:
    GPT_41_NANO_KEY - Azure OpenAI GPT-4.1-nano API Key
    TEXT_EMBEDDING_3_SMALL - Azure OpenAI Embedding API Key
"""

import os
import json
import traceback
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from mem0 import Memory


# ============================================
# Pydantic 数据模型
# ============================================

MY_ROCEDURAL_MEMORY_SYSTEM_PROMPT = """
You are a memory summarization system that records and preserves the complete interaction history between a human and an AI agent. You are provided with the agent’s execution history over the past N steps. Your task is to produce a comprehensive summary of the agent's output history that contains every detail necessary for the agent to continue the task without ambiguity. **Every output produced by the agent must be recorded verbatim as part of the summary.**

### Overall Structure:
- **Overview (Global Metadata):**
  - **Task Objective**: The overall goal the agent is working to accomplish.
  - **Progress Status**: The current completion percentage and summary of specific milestones or steps completed.

- **Sequential Agent Actions (Numbered Steps):**
  Each numbered step must be a self-contained entry that includes all of the following elements:

  1. **Agent Action**:
     - Precisely describe what the agent did (e.g., "Clicked on the 'Blog' link", "Called API to fetch content", "Scraped page data").
     - Include all parameters, target elements, or methods involved.

  2. **Action Result (Mandatory, Unmodified)**:
     - Immediately follow the agent action with its exact, unaltered output.
     - Record all returned data, responses, HTML snippets, JSON content, or error messages exactly as received. This is critical for constructing the final output later.

  3. **Embedded Metadata**:
     For the same numbered step, include additional context such as:
     - **Key Findings**: Any important information discovered (e.g., URLs, data points, search results).
     - **Navigation History**: For browser agents, detail which pages were visited, including their URLs and relevance.
     - **Errors & Challenges**: Document any error messages, exceptions, or challenges encountered along with any attempted recovery or troubleshooting.
     - **Current Context**: Describe the state after the action (e.g., "Agent is on the blog detail page" or "JSON data stored for further processing") and what the agent plans to do next.

### Guidelines:
1. **Preserve Every Output**: The exact output of each agent action is essential. Do not paraphrase or summarize the output. It must be stored as is for later use.
2. **Chronological Order**: Number the agent actions sequentially in the order they occurred. Each numbered step is a complete record of that action.
3. **Detail and Precision**:
   - Use exact data: Include URLs, element indexes, error messages, JSON responses, and any other concrete values.
   - Preserve numeric counts and metrics (e.g., "3 out of 5 items processed").
   - For any errors, include the full error message and, if applicable, the stack trace or cause.
4. **Output Only the Summary**: The final output must consist solely of the structured summary with no additional commentary or preamble.
5. 虽然我下边举的的例子是英文，但你的输出要是用中文

### Example Template:

```
## Summary of the agent's execution history

**Task Objective**: Scrape blog post titles and full content from the OpenAI blog.
**Progress Status**: 10% complete — 5 out of 50 blog posts processed.

1. **Agent Action**: Opened URL "https://openai.com"  
   **Action Result**:  
      "HTML Content of the homepage including navigation bar with links: 'Blog', 'API', 'ChatGPT', etc."  
   **Key Findings**: Navigation bar loaded correctly.  
   **Navigation History**: Visited homepage: "https://openai.com"  
   **Current Context**: Homepage loaded; ready to click on the 'Blog' link.

2. **Agent Action**: Clicked on the "Blog" link in the navigation bar.  
   **Action Result**:  
      "Navigated to 'https://openai.com/blog/' with the blog listing fully rendered."  
   **Key Findings**: Blog listing shows 10 blog previews.  
   **Navigation History**: Transitioned from homepage to blog listing page.  
   **Current Context**: Blog listing page displayed.

3. **Agent Action**: Extracted the first 5 blog post links from the blog listing page.  
   **Action Result**:  
      "[ '/blog/chatgpt-updates', '/blog/ai-and-education', '/blog/openai-api-announcement', '/blog/gpt-4-release', '/blog/safety-and-alignment' ]"  
   **Key Findings**: Identified 5 valid blog post URLs.  
   **Current Context**: URLs stored in memory for further processing.

4. **Agent Action**: Visited URL "https://openai.com/blog/chatgpt-updates"  
   **Action Result**:  
      "HTML content loaded for the blog post including full article text."  
   **Key Findings**: Extracted blog title "ChatGPT Updates – March 2025" and article content excerpt.  
   **Current Context**: Blog post content extracted and stored.

5. **Agent Action**: Extracted blog title and full article content from "https://openai.com/blog/chatgpt-updates"  
   **Action Result**:  
      "{ 'title': 'ChatGPT Updates – March 2025', 'content': 'We\'re introducing new updates to ChatGPT, including improved browsing capabilities and memory recall... (full content)' }"  
   **Key Findings**: Full content captured for later summarization.  
   **Current Context**: Data stored; ready to proceed to next blog post.

... (Additional numbered steps for subsequent actions)
```
"""


class Message(BaseModel):
    """对话消息模型"""
    role: str = Field(..., description="消息角色：user 或 assistant")
    content: str = Field(..., description="消息内容")


class AddMemoryRequest(BaseModel):
    """添加记忆请求"""
    messages: List[Message] = Field(..., description="对话消息列表")
    user_id: str = Field(default="default_user", description="用户 ID")
    agent_id: Optional[str] = Field(default=None, description="Agent ID，用于程序性记忆")
    infer: bool = Field(default=False, description="是否启用推理")
    memory_type: Optional[str] = Field(default=None, description="记忆类型，可选值为 'procedural_memory' 或 None")


class SearchMemoryRequest(BaseModel):
    """搜索记忆请求"""
    query: str = Field(..., description="搜索查询")
    user_id: str = Field(default="default_user", description="用户 ID")
    limit: Optional[int] = Field(default=5, description="返回结果数量限制")


class UpdateMemoryRequest(BaseModel):
    """更新记忆请求"""
    data: str = Field(..., description="新的记忆内容")


class MemoryResponse(BaseModel):
    """记忆响应"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


# ============================================
# 全局变量
# ============================================

memory_instance: Optional[Memory] = None
config: Dict[str, Any] = {}


# ============================================
# 生命周期管理
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global memory_instance, config
    
    # 启动时初始化
    print("=" * 60)
    print("🚀 Mem0 HTTP 服务器启动中...")
    print("=" * 60)
    
    # 禁用遥测
    os.environ["MEM0_TELEMETRY"] = "false"
    
    # 检查环境变量
    gpt_key = os.getenv("GPT_41_NANO_KEY")
    embedding_key = os.getenv("TEXT_EMBEDDING_3_SMALL")
    
    if not gpt_key:
        print("⚠️  警告: 未设置环境变量 GPT_41_NANO_KEY")
    if not embedding_key:
        print("⚠️  警告: 未设置环境变量 TEXT_EMBEDDING_3_SMALL")
    
    # 配置 mem0
    config = {
        # LLM 配置
        "llm": {
            "provider": "azure_openai",
            "config": {
                "model": "gpt-4.1-nano",
                "azure_kwargs": {
                    "api_key": gpt_key,
                    "azure_deployment": "gpt-4.1-nano",
                    "azure_endpoint": "https://bk-us-2.openai.azure.com",
                    "api_version": "2025-01-01-preview",
                }
            }
        },
        # Embedding 配置
        "embedder": {
            "provider": "azure_openai",
            "config": {
                "model": "text-embedding-3-small",
                "embedding_dims": 1536,
                "azure_kwargs": {
                    "api_key": embedding_key,
                    "azure_deployment": "text-embedding-3-small",
                    "azure_endpoint": "https://bk-cloud.openai.azure.com",
                    "api_version": "2023-05-15",
                }
            }
        },
        # 向量存储配置
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "path": "./memorydb/vector",
                "on_disk": True  # 持久化存储
            }
        },
        # 图数据库配置（可选）
        "graph_store": {
            "provider": "kuzu",
            "config": {
                "db": "./memorydb/graph/kemem_graph.db"
            }
        },
        # 历史记录配置
        "history_db_path": "./memorydb/history/history.db"
    }
    
    try:
        memory_instance = Memory.from_config(config_dict=config)
        print("✅ Memory 实例创建成功")
        
        # 显示配置信息
        print(f"📊 向量数据库: Qdrant (路径: ./memorydb/vector)")
        print(f"🔗 图数据库: Kuzu (路径: ./memorydb/graph/kemem_graph.db)")
        print(f"📜 历史记录: SQLite (路径: ./memorydb/history/history.db)")
        
        if hasattr(memory_instance, 'enable_graph'):
            print(f"🔗 图数据库状态: {memory_instance.enable_graph}")
        
        print("=" * 60)
        print("✅ 服务器已就绪！")
        print("📖 访问 http://localhost:8000/docs 查看 API 文档")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        traceback.print_exc()
    
    yield
    
    # 关闭时清理
    print("\n" + "=" * 60)
    print("🛑 Mem0 HTTP 服务器关闭中...")
    print("=" * 60)


# ============================================
# FastAPI 应用
# ============================================

app = FastAPI(
    title="Mem0 记忆管理 API",
    description="提供记忆的增删改查和搜索功能",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================
# API 端点
# ============================================

@app.get("/", response_model=dict)
async def root():
    """根路径 - 服务器信息"""
    return {
        "service": "Mem0 Memory Management API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=dict)
async def health_check():
    """健康检查"""
    if memory_instance is None:
        raise HTTPException(status_code=503, detail="Memory 实例未初始化")
    
    return {
        "status": "healthy",
        "memory_instance": "initialized",
        "graph_enabled": getattr(memory_instance, 'enable_graph', False)
    }


@app.post("/memories", response_model=MemoryResponse)
async def add_memory(request: AddMemoryRequest):
    """
    添加记忆

    - **messages**: 对话消息列表，每条消息包含 role 和 content
    - **user_id**: 用户 ID，用于隔离不同用户的记忆
    - **agent_id**: Agent ID，用于程序性记忆
    - **infer**: 是否启用推理模式
    - **memory_type**: 记忆类型，可选值为 'procedural_memory' 或 None
    """
    if memory_instance is None:
        raise HTTPException(status_code=503, detail="Memory 实例未初始化")

    try:
        # 转换消息格式
        messages = [msg.dict() for msg in request.messages]

        # 添加记忆
        result = memory_instance.add(
            messages=messages,
            user_id=request.user_id,
            agent_id=request.agent_id,
            infer=request.infer,
            memory_type=request.memory_type,
            prompt=MY_ROCEDURAL_MEMORY_SYSTEM_PROMPT
        )

        return MemoryResponse(
            success=True,
            message="记忆添加成功",
            data=result
        )

    except Exception as e:
        return MemoryResponse(
            success=False,
            message=f"添加记忆失败: {str(e)}",
            data={"error": traceback.format_exc()}
        )


@app.post("/memories/search", response_model=MemoryResponse)
async def search_memories(request: SearchMemoryRequest):
    """
    搜索记忆
    
    - **query**: 搜索查询文本
    - **user_id**: 用户 ID
    - **limit**: 返回结果数量限制（默认 5）
    """
    if memory_instance is None:
        raise HTTPException(status_code=503, detail="Memory 实例未初始化")
    
    try:
        # 搜索记忆
        result = memory_instance.search(
            query=request.query,
            user_id=request.user_id,
            limit=request.limit
        )
        
        return MemoryResponse(
            success=True,
            message=f"找到 {len(result.get('results', []))} 条记忆",
            data=result
        )
    
    except Exception as e:
        return MemoryResponse(
            success=False,
            message=f"搜索记忆失败: {str(e)}",
            data={"error": traceback.format_exc()}
        )


@app.get("/memories", response_model=MemoryResponse)
async def get_all_memories(
    user_id: str = Query(default="default_user", description="用户 ID")
):
    """
    获取所有记忆
    
    - **user_id**: 用户 ID
    """
    if memory_instance is None:
        raise HTTPException(status_code=503, detail="Memory 实例未初始化")
    
    try:
        result = memory_instance.get_all(user_id=user_id)
        
        return MemoryResponse(
            success=True,
            message=f"获取到 {len(result.get('results', []))} 条记忆",
            data=result
        )
    
    except Exception as e:
        return MemoryResponse(
            success=False,
            message=f"获取记忆失败: {str(e)}",
            data={"error": traceback.format_exc()}
        )


@app.get("/memories/{memory_id}", response_model=MemoryResponse)
async def get_memory(memory_id: str):
    """
    获取指定 ID 的记忆
    
    - **memory_id**: 记忆 ID
    """
    if memory_instance is None:
        raise HTTPException(status_code=503, detail="Memory 实例未初始化")
    
    try:
        result = memory_instance.get(memory_id=memory_id)
        
        if not result:
            return MemoryResponse(
                success=False,
                message=f"未找到 ID 为 {memory_id} 的记忆",
                data=None
            )
        
        return MemoryResponse(
            success=True,
            message="获取记忆成功",
            data=result
        )
    
    except Exception as e:
        return MemoryResponse(
            success=False,
            message=f"获取记忆失败: {str(e)}",
            data={"error": traceback.format_exc()}
        )


@app.put("/memories/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: str,
    request: UpdateMemoryRequest
):
    """
    更新记忆
    
    - **memory_id**: 记忆 ID
    - **data**: 新的记忆内容
    """
    if memory_instance is None:
        raise HTTPException(status_code=503, detail="Memory 实例未初始化")
    
    try:
        result = memory_instance.update(
            memory_id=memory_id,
            data=request.data
        )
        
        return MemoryResponse(
            success=True,
            message="记忆更新成功",
            data=result
        )
    
    except Exception as e:
        return MemoryResponse(
            success=False,
            message=f"更新记忆失败: {str(e)}",
            data={"error": traceback.format_exc()}
        )


@app.delete("/memories/{memory_id}", response_model=MemoryResponse)
async def delete_memory(memory_id: str):
    """
    删除记忆
    
    - **memory_id**: 记忆 ID
    """
    if memory_instance is None:
        raise HTTPException(status_code=503, detail="Memory 实例未初始化")
    
    try:
        memory_instance.delete(memory_id=memory_id)
        
        return MemoryResponse(
            success=True,
            message=f"记忆 {memory_id} 删除成功",
            data=None
        )
    
    except Exception as e:
        return MemoryResponse(
            success=False,
            message=f"删除记忆失败: {str(e)}",
            data={"error": traceback.format_exc()}
        )


@app.delete("/memories", response_model=MemoryResponse)
async def delete_all_memories(
    user_id: str = Query(default="default_user", description="用户 ID")
):
    """
    删除用户的所有记忆
    
    - **user_id**: 用户 ID
    """
    if memory_instance is None:
        raise HTTPException(status_code=503, detail="Memory 实例未初始化")
    
    try:
        memory_instance.delete_all(user_id=user_id)
        
        return MemoryResponse(
            success=True,
            message=f"用户 {user_id} 的所有记忆已删除",
            data=None
        )
    
    except Exception as e:
        return MemoryResponse(
            success=False,
            message=f"删除记忆失败: {str(e)}",
            data={"error": traceback.format_exc()}
        )


@app.get("/history", response_model=MemoryResponse)
async def get_history(
    user_id: str = Query(default="default_user", description="用户 ID")
):
    """
    获取用户的记忆历史记录（所有记忆列表）

    - **user_id**: 用户 ID
    """
    if memory_instance is None:
        raise HTTPException(status_code=503, detail="Memory 实例未初始化")

    try:
        # 获取用户的所有记忆作为"历史记录"
        result = memory_instance.get_all(user_id=user_id)

        return MemoryResponse(
            success=True,
            message=f"获取到 {len(result.get('results', []))} 条记忆记录",
            data={"history": result.get('results', [])}
        )

    except Exception as e:
        return MemoryResponse(
            success=False,
            message=f"获取历史记录失败: {str(e)}",
            data={"error": traceback.format_exc()}
        )


# ============================================
# 主程序入口
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    # 运行服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )