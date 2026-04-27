import json
import os
from datetime import datetime
from typing import Dict, Any, Optional



"""数据持久化管理器 - 确保所有AI生成内容完整保存"""
class DataPersistence:
    def __init__(self, session_id: str = None):
        self.progress_dir = "progress_logs"
        os.makedirs(self.progress_dir, exist_ok=True)
        if session_id is None:
            self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        else:
            self.session_id = session_id
        self.session_file = os.path.join(self.progress_dir, f"session_{self.session_id}.json")
        # 初始化会话数据结构
        self.session_data = {
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "active",
            "user_query": "",
            "agents_data": {},
            "workflow_state": {},
            "mcp_tool_calls": [],
            "timeline": [],
            "errors": [],
            "warnings": [],
            "metadata": {}
        }
        self._save_session()
    
    def _save_session(self):
        """保存会话数据到JSON文件"""
        try:
            self.session_data["updated_at"] = datetime.now().isoformat()
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass
    
    def save_agent_result(self, agent_name: str, result: Any, metadata: Dict[str, Any] = None):
        """保存智能体完整结果 - 不进行任何截断"""
        if agent_name not in self.session_data["agents_data"]:
            self.session_data["agents_data"][agent_name] = {
                "results": [],
                "actions": [],
                "mcp_calls": [],
                "status": "active",
                "start_time": datetime.now().isoformat()
            }
        
        # 确保完整保存结果，无论长度如何
        result_record = {
            "content": str(result),  # 完整内容，不截断
            "timestamp": datetime.now().isoformat(),
            "content_length": len(str(result)),
            "metadata": metadata or {}
        }
        self.session_data["agents_data"][agent_name]["results"].append(result_record)
        # 添加到时间线
        self._add_timeline_event("agent_result_saved", {
            "agent": agent_name,
            "content_length": len(str(result)),
            "has_metadata": bool(metadata)
        })
        self._save_session()
    
    def save_agent_results(self, agent_name: str, results: Dict[str, Any]):
        """保存智能体结果字典 - 兼容ProgressManager调用"""
        self.save_agent_result(agent_name, results)
    
    def save_mcp_tool_call(self, agent_name: str, tool_name: str, tool_args: Dict, tool_result: Any):
        """保存MCP工具调用的完整结果"""
        tool_call_record = {
            "agent": agent_name,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "tool_result": str(tool_result),  # 完整保存工具结果
            "timestamp": datetime.now().isoformat(),
            "result_length": len(str(tool_result))
        }
        self.session_data["mcp_tool_calls"].append(tool_call_record)
        # 同时保存到对应智能体的记录中
        if agent_name in self.session_data["agents_data"]:
            self.session_data["agents_data"][agent_name]["mcp_calls"].append(tool_call_record)
        self._add_timeline_event("mcp_tool_call", {
            "agent": agent_name,
            "tool": tool_name,
            "result_length": len(str(tool_result))
        })
        self._save_session()
    
    def save_llm_interaction(self, agent_name: str, prompt: str, response: str, metadata: Dict[str, Any] = None):
        """保存LLM交互的完整内容"""
        if agent_name not in self.session_data["agents_data"]:
            self.session_data["agents_data"][agent_name] = {
                "results": [],
                "actions": [],
                "mcp_calls": [],
                "llm_interactions": [],
                "status": "active",
                "start_time": datetime.now().isoformat()
            }
        if "llm_interactions" not in self.session_data["agents_data"][agent_name]:
            self.session_data["agents_data"][agent_name]["llm_interactions"] = []
        interaction_record = {
            "prompt": prompt,  # 完整提示词
            "response": response,  # 完整响应
            "timestamp": datetime.now().isoformat(),
            "prompt_length": len(prompt),
            "response_length": len(response),
            "metadata": metadata or {}
        }
        self.session_data["agents_data"][agent_name]["llm_interactions"].append(interaction_record)
        self._add_timeline_event("llm_interaction", {
            "agent": agent_name,
            "prompt_length": len(prompt),
            "response_length": len(response)
        })
        self._save_session()
    
    def update_agent_status(self, agent_name: str, status: str, metadata: Dict[str, Any] = None):
        """更新智能体状态"""
        if agent_name not in self.session_data["agents_data"]:
            self.session_data["agents_data"][agent_name] = {
                "results": [],
                "actions": [],
                "mcp_calls": [],
                "status": status,
                "start_time": datetime.now().isoformat()
            }
        else:
            self.session_data["agents_data"][agent_name]["status"] = status
        
        if status == "completed":
            self.session_data["agents_data"][agent_name]["end_time"] = datetime.now().isoformat()
        
        if metadata:
            if "metadata" not in self.session_data["agents_data"][agent_name]:
                self.session_data["agents_data"][agent_name]["metadata"] = {}
            self.session_data["agents_data"][agent_name]["metadata"].update(metadata)
        
        self._add_timeline_event("agent_status_update", {
            "agent": agent_name,
            "status": status
        })
        self._save_session()
    
    def save_workflow_state(self, state_data: Dict[str, Any]):
        """保存工作流状态"""
        self.session_data["workflow_state"] = state_data
        self.session_data["workflow_state"]["updated_at"] = datetime.now().isoformat()
        self._add_timeline_event("workflow_state_update", {
            "state_keys": list(state_data.keys())
        })
        self._save_session()
    
    def add_error(self, error_msg: str, agent_name: str = None, context: Dict[str, Any] = None):
        """添加错误记录"""
        error_record = {
            "message": error_msg,
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "context": context or {}
        }
        self.session_data["errors"].append(error_record)
        self._add_timeline_event("error", {
            "agent": agent_name,
            "error_preview": error_msg
        })
        self._save_session()
    
    def add_warning(self, warning_msg: str, agent_name: str = None, context: Dict[str, Any] = None):
        """添加警告记录"""
        warning_record = {
            "message": warning_msg,
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "context": context or {}
        }
        self.session_data["warnings"].append(warning_record)
        self._add_timeline_event("warning", {
            "agent": agent_name,
            "warning_preview": warning_msg
        })
        self._save_session()
    
    def _add_timeline_event(self, event_type: str, event_data: Dict[str, Any]):
        """添加时间线事件"""
        timeline_event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": event_data
        }
        self.session_data["timeline"].append(timeline_event)
    
    def log_workflow_start(self, user_query: str):
        """记录工作流开始"""
        self.session_data["user_query"] = user_query
        self.session_data["start_time"] = datetime.now().isoformat()
        self.session_data["status"] = "running"
        self._add_timeline_event("workflow_start", {
            "query": user_query
        })
        self._save_session()
    
    def log_workflow_completion(self, success: bool = True):
        """记录工作流完成"""
        self.session_data["status"] = "completed" if success else "failed"
        self.session_data["end_time"] = datetime.now().isoformat()
        self._add_timeline_event("workflow_completion", {
            "success": success
        })
        self._save_session()
    
    def log_agent_start(self, agent_name: str, action: str = ""):
        """记录智能体开始工作"""
        if agent_name not in self.session_data["agents_data"]:
            self.session_data["agents_data"][agent_name] = {
                "results": [],
                "actions": [],
                "mcp_calls": [],
                "status": "running",
                "start_time": datetime.now().isoformat()
            }
        else:
            self.session_data["agents_data"][agent_name]["status"] = "running"
            self.session_data["agents_data"][agent_name]["start_time"] = datetime.now().isoformat()
        if action:
            self.add_agent_action(agent_name, action)
        self._add_timeline_event("agent_start", {
            "agent": agent_name,
            "action": action
        })
        self._save_session()
    
    def log_agent_complete(self, agent_name: str, success: bool = True):
        """记录智能体完成工作"""
        if agent_name in self.session_data["agents_data"]:
            self.session_data["agents_data"][agent_name]["status"] = "completed" if success else "failed"
            self.session_data["agents_data"][agent_name]["end_time"] = datetime.now().isoformat()
        self._add_timeline_event("agent_complete", {
            "agent": agent_name,
            "success": success
        })
        self._save_session()
    
    def add_agent_action(self, agent_name: str, action: str, details: Optional[Dict[str, Any]] = None):
        """添加智能体行动记录"""
        if agent_name not in self.session_data["agents_data"]:
            self.session_data["agents_data"][agent_name] = {
                "results": [],
                "actions": [],
                "mcp_calls": [],
                "status": "active",
                "start_time": datetime.now().isoformat()
            }
        action_record = {
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.session_data["agents_data"][agent_name]["actions"].append(action_record)
        self._add_timeline_event("agent_action", {
            "agent": agent_name,
            "action": action
        })
        self._save_session()
    
    def set_user_query(self, query: str):
        """设置用户查询"""
        self.session_data["user_query"] = query
        self._add_timeline_event("user_query_set", {"query": query})
        self._save_session()
    
    def set_final_results(self, results: Dict[str, Any]):
        """设置最终结果"""
        self.session_data["final_results"] = results
        self._add_timeline_event("final_results_set", {
            "result_keys": list(results.keys()) if results else []
        })
        self._save_session()
    
    def update_global_state(self, global_state_data: Dict[str, Any]):
        """更新全局状态"""
        if "global_state" not in self.session_data:
            self.session_data["global_state"] = {}
        self.session_data["global_state"].update(global_state_data)
        self.session_data["global_state"]["updated_at"] = datetime.now().isoformat()
        self._add_timeline_event("global_state_update", {
            "update_keys": list(global_state_data.keys())
        })
        self._save_session()
    
    def update_debate_state(self, debate_type: str, debate_data: Dict[str, Any]):
        """更新辩论状态"""
        if "debates" not in self.session_data:
            self.session_data["debates"] = {}
        if debate_type not in self.session_data["debates"]:
            self.session_data["debates"][debate_type] = {}
        self.session_data["debates"][debate_type].update(debate_data)
        self.session_data["debates"][debate_type]["updated_at"] = datetime.now().isoformat()
        self._add_timeline_event("debate_state_update", {
            "debate_type": debate_type,
            "update_keys": list(debate_data.keys())
        })
        self._save_session()
    
    def finalize_session(self, final_results: Dict[str, Any] = None):
        """完成会话"""
        self.session_data["status"] = "completed"
        self.session_data["completed_at"] = datetime.now().isoformat()
        if final_results:
            self.session_data["final_results"] = final_results
        self._add_timeline_event("session_completed", {
            "total_agents": len(self.session_data["agents_data"]),
            "total_mcp_calls": len(self.session_data["mcp_tool_calls"]),
            "total_errors": len(self.session_data["errors"]),
            "total_warnings": len(self.session_data["warnings"])
        })
        self._save_session()
    
    def get_session_file_path(self) -> str:
        """获取会话文件路径"""
        return self.session_file
    def get_session_data(self) -> Dict[str, Any]:
        """获取完整会话数据"""
        return self.session_data.copy()

    def get_agent_data(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """获取特定智能体的数据"""
        return self.session_data["agents_data"].get(agent_name)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """获取会话摘要"""
        return {
            "session_id": self.session_id,
            "status": self.session_data["status"],
            "created_at": self.session_data["created_at"],
            "updated_at": self.session_data["updated_at"],
            "user_query": self.session_data["user_query"],
            "total_agents": len(self.session_data["agents_data"]),
            "total_mcp_calls": len(self.session_data["mcp_tool_calls"]),
            "total_errors": len(self.session_data["errors"]),
            "total_warnings": len(self.session_data["warnings"]),
            "session_file": self.session_file
        }