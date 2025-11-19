"""
按照要求编写代码：

Mem0 API 客户端测试脚本
用于测试 mem0_server.py 提供的 REST API

构造一些测试用例，用来测试保存 agent 执行状态的，带有 agentid，runid，user_id 的记忆。
比如 "我知道了，我已经保存了 www.baidu.com 的网页，我需要查询一下这个网页的内容。"

使用方法:
    1. 确保 mem0_server.py 正在运行 (python mem0_server.py)
    2. 安装依赖: pip install -r requirements_server.txt
    3. 运行测试: python test_api2_client.py

API 参数说明:
    - user_id: 用户标识，用于隔离不同用户的记忆
    - agent_id: Agent标识，用于程序性记忆和Agent状态跟踪
    - memory_type: 记忆类型
        * None (默认): 普通记忆（语义/情节记忆）
        * "procedural_memory": 程序性记忆（执行流程和步骤）
    - infer: 是否启用LLM推理来提取记忆

测试场景包括:
    - 网页抓取 Agent 执行状态记忆
    - 数据库查询 Agent 执行状态记忆
    - 文件处理 Agent 执行状态记忆
    - 记忆在多次运行间的持久性测试
    - 程序性记忆（Procedural Memory）测试

使用示例:
    # 添加程序性记忆（推荐用于Agent）
    client.add_memory(
        messages=messages,
        user_id="user123",
        agent_id="web_scraper_agent",
        memory_type="procedural_memory",
        infer=True
    )

    # 添加普通记忆
    client.add_memory(
        messages=messages,
        user_id="user123",
        infer=True
    )

"""

import requests
import json
from typing import List, Dict, Any, Optional


class Mem0Client:
    """Mem0 API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def add_memory(
        self,
        messages: List[Dict[str, str]],
        user_id: str = "default_user",
        agent_id: Optional[str] = None,
        infer: bool = False,
        memory_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """添加记忆"""
        data = {
            "messages": messages,
            "user_id": user_id,
            "infer": infer
        }
        if agent_id is not None:
            data["agent_id"] = agent_id
        if memory_type is not None:
            data["memory_type"] = memory_type
        response = requests.post(f"{self.base_url}/memories", json=data)
        return response.json()
    
    def search_memories(
        self,
        query: str,
        user_id: str = "default_user",
        limit: int = 5
    ) -> Dict[str, Any]:
        """搜索记忆"""
        data = {
            "query": query,
            "user_id": user_id,
            "limit": limit
        }
        response = requests.post(f"{self.base_url}/memories/search", json=data)
        return response.json()
    
    def get_all_memories(self, user_id: str = "default_user") -> Dict[str, Any]:
        """获取所有记忆"""
        response = requests.get(f"{self.base_url}/memories", params={"user_id": user_id})
        return response.json()
    
    def get_memory(self, memory_id: str) -> Dict[str, Any]:
        """获取指定记忆"""
        response = requests.get(f"{self.base_url}/memories/{memory_id}")
        return response.json()
    
    def update_memory(self, memory_id: str, data: str) -> Dict[str, Any]:
        """更新记忆"""
        payload = {"data": data}
        response = requests.put(f"{self.base_url}/memories/{memory_id}", json=payload)
        return response.json()
    
    def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """删除记忆"""
        response = requests.delete(f"{self.base_url}/memories/{memory_id}")
        return response.json()
    
    def delete_all_memories(self, user_id: str = "default_user") -> Dict[str, Any]:
        """删除所有记忆"""
        response = requests.delete(f"{self.base_url}/memories", params={"user_id": user_id})
        return response.json()
    
    def get_history(self, user_id: str = "default_user") -> Dict[str, Any]:
        """获取历史记录"""
        response = requests.get(f"{self.base_url}/history", params={"user_id": user_id})
        return response.json()


def print_result(title: str, result: Dict[str, Any]):
    """美化打印结果"""
    print("\n" + "=" * 60)
    print(f"📌 {title}")
    print("=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("=" * 60)


class AgentMemoryTest:
    """Agent 执行状态记忆测试"""

    def __init__(self, client: Mem0Client):
        self.client = client

    def test_agent_webpage_scraping_scenario(self):
        """测试 Agent 网页抓取执行状态记忆场景"""
        print("\n🕷️ 测试 Agent 网页抓取执行状态记忆场景")
        print("=" * 80)

        # 测试用例数据
        agent_id = "web_scraper_agent_001"
        run_id = "run_20241119_001"
        user_id = f"agent_{agent_id}_user_demo"
        memory_type = "procedural_memory"

        # 测试用例 1: Agent 开始执行任务
        print("\n📝 测试用例 1: Agent 开始执行网页抓取任务")
        messages1 = [
            {
                "role": "user",
                "content": f"Agent {agent_id} 开始执行网页抓取任务。运行ID: {run_id}。目标: 保存 www.baidu.com 的网页内容。"
            },
            {
                "role": "assistant",
                "content": f"收到任务。我将开始抓取 www.baidu.com 的网页内容。Agent ID: {agent_id}, Run ID: {run_id}。"
            }
        ]
        print("原始 messages: ", messages1)

        result1 = self.client.add_memory(messages1, user_id=user_id, agent_id=agent_id, infer=True, memory_type=memory_type)
        print_result("Agent 开始任务记忆", result1)

        # 测试用例 2: Agent 执行中 - 发现内容
        print("\n📝 测试用例 2: Agent 执行中 - 发现并保存网页内容")
        messages2 = [
            {
                "role": "user",
                "content": f"Agent {agent_id} 正在抓取 www.baidu.com，已发现主要内容：百度搜索首页，包含搜索框、导航栏等。"
            },
            {
                "role": "assistant",
                "content": f"我知道了，我已经保存了 www.baidu.com 的网页内容。Agent ID: {agent_id}, Run ID: {run_id}。内容包括：百度搜索首页，搜索框，导航栏，热门搜索等。"
            }
        ]
        print("原始 messages: ", messages2)

        result2 = self.client.add_memory(messages2, user_id=user_id, agent_id=agent_id, infer=True, memory_type=memory_type)
        print_result("Agent 保存网页内容记忆", result2)

        # 测试用例 3: Agent 完成任务
        print("\n📝 测试用例 3: Agent 完成网页抓取任务")
        messages3 = [
            {
                "role": "user",
                "content": f"Agent {agent_id} 完成了 www.baidu.com 的网页抓取任务。运行ID: {run_id} 执行完毕。"
            },
            {
                "role": "assistant",
                "content": f"任务完成！我已经成功保存了 www.baidu.com 的完整网页内容。Agent ID: {agent_id}, Run ID: {run_id}。"
            }
        ]
        print("原始 messages: ", messages3)

        result3 = self.client.add_memory(messages3, user_id=user_id, agent_id=agent_id, infer=True, memory_type=memory_type)
        print_result("Agent 完成任务记忆", result3)

        # 测试用例 4: 搜索相关记忆
        print("\n📝 测试用例 4: 搜索 Agent 执行状态记忆")
        query="www.baidu.com 网页内容"
        search_result = self.client.search_memories(
            query=query,
            user_id=user_id,
            limit=10
        )
        print_result(f"搜索 \"{query}\" 记忆", search_result)

        # 测试用例 5: 查询特定 Agent 的执行历史
        print("\n📝 测试用例 5: 查询 Agent 执行历史")
        history_result = self.client.get_history(user_id=user_id)
        print_result("Agent 执行历史", history_result)

        return {
            "agent_id": agent_id,
            "run_id": run_id,
            "user_id": user_id,
            "results": [result1, result2, result3, search_result, history_result]
        }

    def test_agent_database_query_scenario(self):
        """测试 Agent 数据库查询执行状态记忆场景"""
        print("\n🗄️ 测试 Agent 数据库查询执行状态记忆场景")
        print("=" * 80)

        agent_id = "db_query_agent_002"
        run_id = "run_20241119_002"
        user_id = f"agent_{agent_id}_user_demo"

        # 测试用例 1: Agent 开始数据库查询
        print("\n📝 测试用例 1: Agent 开始数据库查询任务")
        messages1 = [
            {
                "role": "user",
                "content": f"Agent {agent_id} 开始执行数据库查询任务。运行ID: {run_id}。查询用户表中的活跃用户数据。"
            },
            {
                "role": "assistant",
                "content": f"开始执行数据库查询。Agent ID: {agent_id}, Run ID: {run_id}。目标：查询活跃用户数据。"
            }
        ]

        result1 = self.client.add_memory(messages1, user_id=user_id, infer=True)
        print_result("Agent 开始查询记忆", result1)

        # 测试用例 2: Agent 执行查询并获取结果
        print("\n📝 测试用例 2: Agent 执行查询并保存结果")
        messages2 = [
            {
                "role": "user",
                "content": f"Agent {agent_id} 已执行查询，发现数据库中有 1250 个活跃用户，最近7天登录的有 890 个用户。"
            },
            {
                "role": "assistant",
                "content": f"我知道了，我已经查询并保存了用户数据库的状态。Agent ID: {agent_id}, Run ID: {run_id}。活跃用户总数：1250，7天内登录：890。"
            }
        ]

        result2 = self.client.add_memory(messages2, user_id=user_id, infer=True)
        print_result("Agent 保存查询结果记忆", result2)

        # 测试用例 3: 搜索数据库相关记忆
        print("\n📝 测试用例 3: 搜索数据库查询记忆")
        search_result = self.client.search_memories(
            query="活跃用户 数据库查询",
            user_id=user_id,
            limit=10
        )
        print_result("搜索数据库查询记忆", search_result)

        return {
            "agent_id": agent_id,
            "run_id": run_id,
            "user_id": user_id,
            "results": [result1, result2, search_result]
        }

    def test_agent_file_processing_scenario(self):
        """测试 Agent 文件处理执行状态记忆场景"""
        print("\n📁 测试 Agent 文件处理执行状态记忆场景")
        print("=" * 80)

        agent_id = "file_processor_agent_003"
        run_id = "run_20241119_003"
        user_id = f"agent_{agent_id}_user_demo"

        # 测试用例 1: Agent 开始文件处理
        print("\n📝 测试用例 1: Agent 开始文件处理任务")
        messages1 = [
            {
                "role": "user",
                "content": f"Agent {agent_id} 开始处理上传的文件。运行ID: {run_id}。文件：report.pdf，大小：2.5MB。"
            },
            {
                "role": "assistant",
                "content": f"开始处理文件 report.pdf。Agent ID: {agent_id}, Run ID: {run_id}。"
            }
        ]

        result1 = self.client.add_memory(messages1, user_id=user_id, infer=True)
        print_result("Agent 开始文件处理记忆", result1)

        # 测试用例 2: Agent 解析文件内容
        print("\n📝 测试用例 2: Agent 解析并保存文件内容")
        messages2 = [
            {
                "role": "user",
                "content": f"Agent {agent_id} 已解析 report.pdf 文件，发现包含销售数据表格和图表分析。"
            },
            {
                "role": "assistant",
                "content": f"我知道了，我已经解析并保存了 report.pdf 文件的内容。Agent ID: {agent_id}, Run ID: {run_id}。内容包括销售数据和分析图表。"
            }
        ]

        result2 = self.client.add_memory(messages2, user_id=user_id, infer=True)
        print_result("Agent 保存文件内容记忆", result2)

        # 测试用例 3: Agent 生成处理报告
        print("\n📝 测试用例 3: Agent 生成处理报告")
        messages3 = [
            {
                "role": "user",
                "content": f"Agent {agent_id} 完成了文件处理，生成了分析报告。运行ID: {run_id} 执行完毕。"
            },
            {
                "role": "assistant",
                "content": f"文件处理完成！我已经生成了完整的分析报告。Agent ID: {agent_id}, Run ID: {run_id}。"
            }
        ]

        result3 = self.client.add_memory(messages3, user_id=user_id, infer=True)
        print_result("Agent 完成处理记忆", result3)

        # 测试用例 4: 搜索文件处理记忆
        print("\n📝 测试用例 4: 搜索文件处理记忆")
        search_result = self.client.search_memories(
            query="report.pdf 文件处理",
            user_id=user_id,
            limit=10
        )
        print_result("搜索文件处理记忆", search_result)

        return {
            "agent_id": agent_id,
            "run_id": run_id,
            "user_id": user_id,
            "results": [result1, result2, result3, search_result]
        }

    def test_memory_persistence_across_runs(self):
        """测试记忆在多次运行间的持久性"""
        print("\n🔄 测试记忆在多次运行间的持久性")
        print("=" * 80)

        agent_id = "persistent_agent_004"
        user_id = f"agent_{agent_id}_user_demo"

        # 第一次运行
        run_id_1 = "run_20241119_004a"
        print(f"\n📝 第一次运行: {run_id_1}")
        messages1 = [
            {
                "role": "user",
                "content": f"Agent {agent_id} 第一次运行。运行ID: {run_id_1}。学习用户偏好：喜欢科技新闻。"
            },
            {
                "role": "assistant",
                "content": f"已记录用户偏好。Agent ID: {agent_id}, Run ID: {run_id_1}。用户喜欢科技新闻。"
            }
        ]

        result1 = self.client.add_memory(messages1, user_id=user_id, infer=True)
        print_result("第一次运行记忆", result1)

        # 第二次运行 - 应该能回忆起之前的偏好
        run_id_2 = "run_20241119_004b"
        print(f"\n📝 第二次运行: {run_id_2}")
        messages2 = [
            {
                "role": "user",
                "content": f"Agent {agent_id} 第二次运行。运行ID: {run_id_2}。需要推荐新闻内容。"
            },
            {
                "role": "assistant",
                "content": f"根据之前的记忆，用户喜欢科技新闻。Agent ID: {agent_id}, Run ID: {run_id_2}。"
            }
        ]

        result2 = self.client.add_memory(messages2, user_id=user_id, infer=True)
        print_result("第二次运行记忆", result2)

        # 搜索所有相关记忆
        print("\n📝 搜索所有运行记忆")
        search_result = self.client.search_memories(
            query="科技新闻 用户偏好",
            user_id=user_id,
            limit=10
        )
        print_result("搜索跨运行记忆", search_result)

        return {
            "agent_id": agent_id,
            "user_id": user_id,
            "runs": [run_id_1, run_id_2],
            "results": [result1, result2, search_result]
        }

    def test_procedural_memory_scenario(self):
        """测试程序性记忆（Procedural Memory）"""
        print("\n🧠 测试程序性记忆（Procedural Memory）")
        print("=" * 80)

        agent_id = "procedural_agent_005"
        run_id = "run_20241119_005"
        user_id = f"agent_{agent_id}_user_demo"

        # 测试用例 1: 添加程序性记忆 - 学习如何执行任务
        print("\n📝 测试用例 1: 添加程序性记忆 - 学习网页抓取流程")
        messages1 = [
            {
                "role": "user",
                "content": f"Agent {agent_id} 学习网页抓取流程。运行ID: {run_id}。"
            },
            {
                "role": "assistant",
                "content": f"学习中。Agent ID: {agent_id}, Run ID: {run_id}。程序性记忆：1. 发送HTTP请求 2. 解析HTML 3. 提取数据 4. 保存结果。"
            }
        ]

        result1 = self.client.add_memory(
            messages1,
            user_id=user_id,
            agent_id=agent_id,
            infer=True,
            memory_type="procedural_memory"
        )
        print_result("添加程序性记忆 - 网页抓取流程", result1)

        # 测试用例 2: 添加程序性记忆 - 学习数据处理步骤
        print("\n📝 测试用例 2: 添加程序性记忆 - 学习数据处理步骤")
        messages2 = [
            {
                "role": "user",
                "content": f"Agent {agent_id} 学习数据处理步骤。运行ID: {run_id}。"
            },
            {
                "role": "assistant",
                "content": f"学习中。Agent ID: {agent_id}, Run ID: {run_id}。程序性记忆：1. 验证数据格式 2. 清理无效数据 3. 转换数据类型 4. 存储到数据库。"
            }
        ]

        result2 = self.client.add_memory(
            messages2,
            user_id=user_id,
            agent_id=agent_id,
            infer=True,
            memory_type="procedural_memory"
        )
        print_result("添加程序性记忆 - 数据处理步骤", result2)

        # 测试用例 3: 添加普通记忆进行对比
        print("\n📝 测试用例 3: 添加普通记忆进行对比")
        messages3 = [
            {
                "role": "user",
                "content": f"Agent {agent_id} 记录执行结果。运行ID: {run_id}。"
            },
            {
                "role": "assistant",
                "content": f"执行完成。Agent ID: {agent_id}, Run ID: {run_id}。成功处理了100条数据记录。"
            }
        ]

        result3 = self.client.add_memory(
            messages3,
            user_id=user_id,
            agent_id=agent_id,
            infer=True,
            memory_type=None  # 普通记忆
        )
        print_result("添加普通记忆 - 执行结果", result3)

        # 测试用例 4: 搜索程序性记忆
        print("\n📝 测试用例 4: 搜索程序性记忆")
        search_procedural = self.client.search_memories(
            query="网页抓取流程 数据处理步骤",
            user_id=user_id,
            limit=10
        )
        print_result("搜索程序性记忆", search_procedural)

        # 测试用例 5: 搜索普通记忆
        print("\n📝 测试用例 5: 搜索普通记忆")
        search_regular = self.client.search_memories(
            query="执行结果 数据记录",
            user_id=user_id,
            limit=10
        )
        print_result("搜索普通记忆", search_regular)

        return {
            "agent_id": agent_id,
            "run_id": run_id,
            "user_id": user_id,
            "results": [result1, result2, result3, search_procedural, search_regular]
        }


def run_all_tests():
    """运行所有测试用例"""
    print("🚀 开始运行 Mem0 API Agent 执行状态记忆测试")
    print("=" * 80)

    # 初始化客户端
    client = Mem0Client()

    # 健康检查
    print("\n🏥 执行健康检查...")
    try:
        health = client.health_check()
        print_result("健康检查", health)
        if not health.get("status") == "healthy":
            print("❌ 服务器健康检查失败，请确保 mem0_server.py 正在运行")
            return
    except Exception as e:
        print(f"❌ 连接服务器失败: {e}")
        print("请确保 mem0_server.py 正在运行在 http://localhost:8000")
        return

    # 初始化测试器
    tester = AgentMemoryTest(client)

    # 运行所有测试场景
    test_results = {}

    try:
        print("\n🎯 开始执行测试场景...")

        # 测试场景 1: 网页抓取
        test_results["web_scraping"] = tester.test_agent_webpage_scraping_scenario()

        # 测试场景 2: 数据库查询
        #test_results["database_query"] = tester.test_agent_database_query_scenario()

        # 测试场景 3: 文件处理
        #test_results["file_processing"] = tester.test_agent_file_processing_scenario()

        # 测试场景 4: 记忆持久性
        #test_results["memory_persistence"] = tester.test_memory_persistence_across_runs()

        # 测试场景 5: 程序性记忆
        #test_results["procedural_memory"] = tester.test_procedural_memory_scenario()

        # 生成测试报告
        print("\n📊 生成测试报告")
        print("=" * 80)

        total_scenarios = len(test_results)
        successful_scenarios = sum(1 for result in test_results.values() if all(r.get("success", False) for r in result["results"]))

        print(f"📈 测试完成统计:")
        print(f"   总测试场景数: {total_scenarios}")
        print(f"   成功场景数: {successful_scenarios}")
        print(f"   失败场景数: {total_scenarios - successful_scenarios}")

        if successful_scenarios == total_scenarios:
            print("✅ 所有测试场景均通过！Agent 执行状态记忆功能正常。")
        else:
            print("⚠️ 部分测试场景失败，请检查服务器日志。")

        # 显示各场景结果摘要
        print(f"\n📋 测试场景结果摘要:")
        for scenario_name, scenario_result in test_results.items():
            success_count = sum(1 for r in scenario_result["results"] if r.get("success", False))
            total_count = len(scenario_result["results"])
            status = "✅" if success_count == total_count else "❌"
            print(f"   {status} {scenario_name}: {success_count}/{total_count} 成功")

    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()

    return test_results


if __name__ == "__main__":
    # 运行所有测试
    run_all_tests()

