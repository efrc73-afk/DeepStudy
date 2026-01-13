"""
聊天相关路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from backend.api.schemas.request import ChatRequest
from backend.api.schemas.response import AgentResponse, DialogueNodeBase, ErrorResponse
from backend.api.middleware.auth import get_current_user_id
from backend.agent.orchestrator import AgentOrchestrator
from backend.data.sqlite_db import get_db, save_conversation, get_conversation_tree


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=AgentResponse)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    发送聊天消息（支持普通提问和划词追问）
    
    Args:
        request: 聊天请求（包含 query, parent_id, ref_fragment_id, session_id）
        user_id: 当前用户 ID
        
    Returns:
        Agent 响应
    """
    try:
        orchestrator = AgentOrchestrator()
        
        # 判断是否为划词追问
        if request.ref_fragment_id:
            # 递归追问
            response = await orchestrator.process_recursive_query(
                user_id=user_id,
                parent_id=request.parent_id or "",
                fragment_id=request.ref_fragment_id,
                query=request.query
            )
        else:
            # 普通提问
            response = await orchestrator.process_query(
                user_id=user_id,
                query=request.query,
                parent_id=request.parent_id,
                session_id=request.session_id
            )
        
        # 保存对话记录
        db = await get_db()
        await save_conversation(
            db,
            user_id=user_id,
            conversation_id=response.conversation_id,
            parent_id=request.parent_id or None,
            query=request.query,
            answer=response.answer
        )
        
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理请求时出错: {str(e)}"
        )


@router.get("/conversation/{conversation_id}", response_model=DialogueNodeBase)
async def get_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    获取对话树
    
    Args:
        conversation_id: 对话 ID
        user_id: 当前用户 ID
        
    Returns:
        对话树节点
    """
    db = await get_db()
    tree = await get_conversation_tree(db, conversation_id, user_id)
    
    if not tree:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    return tree
