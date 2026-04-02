import json
import os
import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional


class ProgressTracker:
    """简化的进度跟踪器 - 输出核心agent结果并保存到JSON"""
    
    def __init__(self, session_id: str = None):
        # 生成强唯一的会话ID：微秒 + UUID短码，避免并发同秒冲突
        self.session_id = session_id or f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{uuid.uuid4().hex[:8]}"
        self.current_stage = ""
        self.current_agent = ""
        # 初始化dump文件夹和JSON文件
        self.dump_dir = os.path.join(os.path.dirname(__file__), "dump")
        os.makedirs(self.dump_dir, exist_ok=True)
        self.json_file = os.path.join(self.dump_dir, f"session_{self.session_id}.json")
        # 初始化JSON数据结构
        self.session_data = {
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "active",
            "user_query": "",
            "active_agents": [],
            "stages": [],
            "agents": [],
            "actions": [],
            "mcp_calls": [],
            "errors": [],
            "warnings": [],
            "final_results": {}
        }
        # 首次写入时确保原子创建，若意外存在则重新生成ID
        self._init_json_file()
    
    def _init_json_file(self):
        """原子创建JSON文件，避免并发命名冲突。"""
        try:
            # 尝试独占创建；如已存在则换一个ID
            while True:
                try:
                    with open(self.json_file, 'x', encoding='utf-8') as f:
                        json.dump(self.session_data, f, ensure_ascii=False, indent=2)
                    break
                except FileExistsError:
                    # 极小概率碰撞，重生成ID与路径
                    self.session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{uuid.uuid4().hex[:8]}"
                    self.json_file = os.path.join(self.dump_dir, f"session_{self.session_id}.json")
        except Exception as e:
            pass

    def _save_json(self):
        """保存数据到JSON文件（Windows友好：带重试的原子替换，必要时回退为直接写）。"""
        self.session_data["updated_at"] = datetime.now().isoformat()
        tmp_path = f"{self.json_file}.{uuid.uuid4().hex}.tmp"
        try:
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            return

        # Windows 下 os.replace 可能因目的文件被读取而临时拒绝访问；重试几次
        replaced = False
        for i in range(6):  # ~ 累计约 1.5 秒
            try:
                os.replace(tmp_path, self.json_file)
                replaced = True
                break
            except PermissionError as e:
                # 回退等待后重试
                time.sleep(0.25 * (i + 1))
            except Exception as e:
                break
        if not replaced:
            # 回退：直接覆盖写入目标（可能不是全原子，但尽量保证成功）
            try:
                with open(self.json_file, 'w', encoding='utf-8') as f:
                    json.dump(self.session_data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                pass
            finally:
                # 清理残留临时文件
                try:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                except Exception:
                    pass
    
    def update_user_query(self, query: str):
        """更新用户查询"""
        self.session_data["user_query"] = query
        self._save_json()

    def set_active_agents(self, active_agents):
        """记录本轮启用的智能体列表"""
        try:
            self.session_data["active_agents"] = list(active_agents or [])
            self._save_json()
        except Exception:
            pass
    
    def start_stage(self, stage_name: str, description: str = ""):
        """开始新阶段"""
        self.current_stage = stage_name
        stage_data = {
            "stage_name": stage_name,
            "description": description,
            "start_time": datetime.now().isoformat()
        }
        self.session_data["stages"].append(stage_data)
        self._save_json()
    
    def start_agent(self, agent_name: str, action: str = "", system_prompt: str = "", user_prompt: str = "", context: str = ""):
        """开始智能体工作"""
        self.current_agent = agent_name
        agent_data = {
            "agent_name": agent_name,
            "action": action,
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "result": "",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt, 
            "context": context
        }
        self.session_data["agents"].append(agent_data)
        self._save_json()
    
    def complete_agent(self, agent_name: str, result: str = "", success: bool = True):
        """完成智能体工作"""
        # 更新对应的agent记录
        for agent in self.session_data["agents"]:
            if agent["agent_name"] == agent_name and agent["status"] == "running":
                agent["status"] = "completed" if success else "failed"
                agent["result"] = result
                agent["end_time"] = datetime.now().isoformat()
                break

        self._save_json()
    
    def add_agent_action(self, agent_name: str, action: str, details: Dict[str, Any] = None):
        """添加智能体行动记录"""
        action_data = {
            "agent_name": agent_name,
            "action": action,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.session_data["actions"].append(action_data)
        self._save_json()
    
    def add_mcp_tool_call(self, agent_name: str, tool_name: str, tool_args: Dict, tool_result: Any):
        """记录MCP工具调用"""
        mcp_data = {
            "agent_name": agent_name,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "tool_result": str(tool_result),
            "timestamp": datetime.now().isoformat()
        }
        self.session_data["mcp_calls"].append(mcp_data)
        self._save_json()
    
    def update_global_state(self, state_key: str, state_value: Any):
        """更新全局状态"""
        pass  # 简化：不再保存状态
    
    def update_debate_state(self, debate_type: str, debate_data: Dict[str, Any]):
        """更新辩论状态"""
        pass
    
    def add_error(self, error_msg: str, agent_name: str = None):
        """添加错误记录"""
        error_data = {
            "error_msg": error_msg,
            "agent_name": agent_name or "",
            "timestamp": datetime.now().isoformat()
        }
        self.session_data["errors"].append(error_data)
        self._save_json()
    
    def add_warning(self, warning_msg: str, agent_name: str = None):
        """添加警告记录"""
        warning_data = {
            "warning_msg": warning_msg,
            "agent_name": agent_name or "",
            "timestamp": datetime.now().isoformat()
        }
        self.session_data["warnings"].append(warning_data)
        self._save_json()
    
    def set_final_results(self, results: Dict[str, Any]):
        """设置最终结果"""
        self.session_data["final_results"] = results
        self.session_data["status"] = "completed"
        self._save_json()
    
    def log_workflow_start(self, workflow_info: Dict[str, Any]):
        """记录工作流开始"""
        pass
    
    def log_workflow_completion(self, completion_info: Dict[str, Any]):
        """记录工作流完成"""
        pass
    
    def log_agent_start(self, agent_name: str, context: Dict[str, Any] = None):
        """记录智能体开始工作"""
        self.start_agent(agent_name, context.get("action", "") if context else "")
    
    def log_agent_complete(self, agent_name: str, result: Any = None, context: Dict[str, Any] = None):
        """记录智能体完成工作"""
        result_str = str(result) if result else ""
        success = context.get("success", True) if context else True
        self.complete_agent(agent_name, result_str, success)
    
    def log_llm_call(self, agent_name: str, prompt_preview: str, context: Dict[str, Any] = None):
        """记录LLM调用"""
        self.add_agent_action(agent_name, "LLM调用")
    
    def log_error(self, agent_name: str, error: str, context: Dict[str, Any] = None):
        """记录错误"""
        self.add_error(error, agent_name)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """获取会话摘要"""
        return {"session_id": self.session_id}