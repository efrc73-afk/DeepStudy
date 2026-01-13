"""
思维导图相关路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from backend.api.schemas.response import MindMapGraph
from backend.api.middleware.auth import get_current_user_id
from backend.data.neo4j_client import neo4j_client


router = APIRouter(prefix="/mindmap", tags=["mindmap"])


@router.get("/{conversation_id}", response_model=MindMapGraph)
async def get_mind_map(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    获取思维导图数据
    
    Args:
        conversation_id: 对话 ID
        user_id: 当前用户 ID
        
    Returns:
        思维导图数据
    """
    # TODO: 从 Neo4j 获取知识图谱数据并转换为 ReactFlow 格式
    # 这里先返回空数据
    return MindMapGraph(nodes=[], edges=[])
