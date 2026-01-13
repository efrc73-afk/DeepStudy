"""
Agent 编排器
使用 LlamaIndex 编排对话流程
"""
import uuid
from typing import Optional
from llama_index.llms.modelscope import ModelScopeLLM
from backend.agent.intent_router import IntentRouter, IntentType
from backend.agent.strategies import DerivationStrategy, CodeStrategy, ConceptStrategy
from backend.agent.prompts.system_prompts import RECURSIVE_PROMPT
from backend.api.schemas.response import AgentResponse
from backend.config import settings


class AgentOrchestrator:
    """
    Agent 编排器
    负责协调意图识别、策略选择和响应生成
    """
    
    def __init__(self):
        """初始化编排器"""
        # 初始化主模型
        self.llm = ModelScopeLLM(
            model_name=settings.MODEL_NAME,
            api_key=settings.MODELSCOPE_API_KEY,
            api_base=settings.MODELSCOPE_API_BASE
        )
        
        # 初始化 Coder 模型（用于代码型问题）
        self.coder_llm = ModelScopeLLM(
            model_name=settings.CODER_MODEL_NAME,
            api_key=settings.MODELSCOPE_API_KEY,
            api_base=settings.MODELSCOPE_API_BASE
        )
        
        # 初始化意图路由器
        self.intent_router = IntentRouter(self.llm)
        
        # 初始化策略
        self.strategies = {
            IntentType.DERIVATION: DerivationStrategy(self.llm),
            IntentType.CODE: CodeStrategy(self.coder_llm),
            IntentType.CONCEPT: ConceptStrategy(self.llm),
        }
    
    async def process_query(
        self,
        user_id: str,
        query: str,
        parent_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> AgentResponse:
        """
        处理用户查询
        
        Args:
            user_id: 用户 ID
            query: 用户查询
            parent_id: 父对话 ID（可选）
            
        Returns:
            Agent 响应
        """
        # 识别意图
        intent = await self.intent_router.route(query)
        
        # 选择策略
        strategy = self.strategies[intent]
        
        # 处理查询
        context = {
            "user_id": user_id,
            "parent_id": parent_id,
        }
        response = await strategy.process(query, context)
        
        # 生成对话 ID
        response.conversation_id = str(uuid.uuid4())
        response.parent_id = parent_id
        
        # TODO: 提取知识三元组
        # TODO: 提取文本片段
        # TODO: 生成思维导图数据
        
        return response
    
    async def process_recursive_query(
        self,
        user_id: str,
        parent_id: str,
        fragment_id: str,
        query: str
    ) -> AgentResponse:
        """
        处理递归追问
        
        Args:
            user_id: 用户 ID
            parent_id: 父对话 ID
            fragment_id: 选中的文本片段 ID
            query: 追问内容
            
        Returns:
            Agent 响应
        """
        # TODO: 获取父对话上下文
        # TODO: 获取片段内容
        
        # 使用递归提示词
        prompt = f"{RECURSIVE_PROMPT}\n\n用户追问: {query}\n\n请针对性地回答："
        
        response_text = await self.llm.acomplete(prompt)
        answer = response_text.text if hasattr(response_text, 'text') else str(response_text)
        
        return AgentResponse(
            answer=answer,
            fragments=[],
            knowledge_triples=[],
            conversation_id=str(uuid.uuid4()),
            parent_id=parent_id
        )
