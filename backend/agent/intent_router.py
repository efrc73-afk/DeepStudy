"""
意图识别与路由
识别用户意图（推导/代码/概念），调用不同的处理策略
"""
from enum import Enum
from typing import Dict, Any
from llama_index.llms.base import LLM
from backend.config import settings


class IntentType(str, Enum):
    """意图类型"""
    DERIVATION = "derivation"  # 推导型
    CODE = "code"  # 代码型
    CONCEPT = "concept"  # 概念型


class IntentRouter:
    """
    意图路由器
    使用 Few-shot 提示词识别用户意图
    """
    
    def __init__(self, llm: LLM):
        """
        初始化意图路由器
        
        Args:
            llm: 大语言模型实例
        """
        self.llm = llm
        self.few_shot_examples = self._get_few_shot_examples()
    
    def _get_few_shot_examples(self) -> str:
        """获取 Few-shot 示例"""
        return """
示例1:
问题: "为什么矩阵的特征值等于其行列式的值？"
意图: derivation

示例2:
问题: "用 Python 实现快速排序"
意图: code

示例3:
问题: "什么是 Schur 分解？"
意图: concept
"""
    
    async def route(self, query: str) -> IntentType:
        """
        识别用户意图
        
        Args:
            query: 用户查询
            
        Returns:
            意图类型
        """
        prompt = f"""
{self.few_shot_examples}

请根据以下问题判断意图类型（derivation/code/concept）:

问题: "{query}"
意图: 
"""
        
        try:
            response = await self.llm.acomplete(prompt)
            intent_str = response.text.strip().lower()
            
            # 解析意图
            if "code" in intent_str or "代码" in intent_str:
                return IntentType.CODE
            elif "derivation" in intent_str or "推导" in intent_str:
                return IntentType.DERIVATION
            else:
                return IntentType.CONCEPT
        except Exception:
            # 默认返回概念型
            return IntentType.CONCEPT
