"""
Neo4j 知识图谱客户端
管理知识图谱的节点和关系
"""
from typing import List, Dict, Optional
from datetime import datetime
from neo4j import AsyncGraphDatabase
from backend.config import settings


class Neo4jClient:
    """Neo4j 客户端"""
    
    def __init__(self):
        """初始化 Neo4j 客户端"""
        self.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
    
    async def close(self):
        """关闭连接"""
        await self.driver.close()
    
    async def create_node(
        self,
        label: str,
        properties: Dict
    ) -> str:
        """
        创建节点
        
        Args:
            label: 节点标签
            properties: 节点属性
            
        Returns:
            节点 ID
        """
        async with self.driver.session() as session:
            result = await session.run(
                f"CREATE (n:{label} $properties) RETURN id(n) as node_id",
                properties=properties
            )
            record = await result.single()
            return str(record["node_id"])
    
    async def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: Optional[Dict] = None
    ):
        """
        创建关系
        
        Args:
            source_id: 源节点 ID
            target_id: 目标节点 ID
            relation_type: 关系类型
            properties: 关系属性（可选）
        """
        async with self.driver.session() as session:
            query = f"""
            MATCH (a), (b)
            WHERE id(a) = $source_id AND id(b) = $target_id
            CREATE (a)-[r:{relation_type}"""
            
            if properties:
                query += " $properties"
                query += "]->(b)"
                await session.run(
                    query,
                    source_id=int(source_id),
                    target_id=int(target_id),
                    properties=properties
                )
            else:
                query += "]->(b)"
                await session.run(
                    query,
                    source_id=int(source_id),
                    target_id=int(target_id)
                )
    
    async def get_node_by_name(
        self,
        label: str,
        name: str
    ) -> Optional[Dict]:
        """
        根据名称获取节点
        
        Args:
            label: 节点标签
            name: 节点名称
            
        Returns:
            节点信息字典，如果不存在则返回 None
        """
        async with self.driver.session() as session:
            result = await session.run(
                f"MATCH (n:{label} {{name: $name}}) RETURN n, id(n) as node_id",
                name=name
            )
            record = await result.single()
            if record:
                node = dict(record["n"])
                node["id"] = str(record["node_id"])
                return node
            return None
    
    async def get_related_nodes(
        self,
        node_id: str,
        relation_type: Optional[str] = None
    ) -> List[Dict]:
        """
        获取相关节点
        
        Args:
            node_id: 节点 ID
            relation_type: 关系类型（可选）
            
        Returns:
            相关节点列表
        """
        async with self.driver.session() as session:
            if relation_type:
                query = f"""
                MATCH (a)-[r:{relation_type}]->(b)
                WHERE id(a) = $node_id
                RETURN b, id(b) as node_id, type(r) as relation
                """
                result = await session.run(
                    query,
                    node_id=int(node_id)
                )
            else:
                result = await session.run(
                    """
                    MATCH (a)-[r]->(b)
                    WHERE id(a) = $node_id
                    RETURN b, id(b) as node_id, type(r) as relation
                    """,
                    node_id=int(node_id)
                )
            
            records = await result.values()
            nodes = []
            for record in records:
                node = dict(record[0])
                node["id"] = str(record[1])
                node["relation"] = record[2]
                nodes.append(node)
            return nodes
    
    async def save_dialogue_node(
        self,
        node_id: str,
        user_id: str,
        role: str,
        content: str,
        intent: Optional[str] = None,
        mastery_score: float = 0.0,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        保存对话节点
        
        Args:
            node_id: 节点唯一标识（UUID）
            user_id: 用户 ID
            role: 角色（"user" 或 "assistant"）
            content: 对话内容
            intent: 意图类型（可选）
            mastery_score: 掌握度评分（0-1）
            timestamp: 时间戳（可选，默认当前时间）
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        async with self.driver.session() as session:
            await session.run(
                """
                MERGE (n:DialogueNode {node_id: $node_id})
                SET n.user_id = $user_id,
                    n.role = $role,
                    n.content = $content,
                    n.intent = $intent,
                    n.mastery_score = $mastery_score,
                    n.timestamp = $timestamp
                """,
                node_id=node_id,
                user_id=user_id,
                role=role,
                content=content,
                intent=intent,
                mastery_score=mastery_score,
                timestamp=timestamp.isoformat()
            )
    
    async def link_dialogue_nodes(
        self,
        parent_node_id: str,
        child_node_id: str,
        fragment_id: Optional[str] = None
    ) -> None:
        """
        创建对话节点之间的父子关系
        
        Args:
            parent_node_id: 父节点 ID
            child_node_id: 子节点 ID
            fragment_id: 片段 ID（可选，用于划词追问）
        """
        async with self.driver.session() as session:
            # 检查节点是否存在
            parent_check = await session.run(
                "MATCH (n:DialogueNode {node_id: $node_id}) RETURN n",
                node_id=parent_node_id
            )
            if not await parent_check.single():
                raise ValueError(f"父节点不存在: {parent_node_id}")
            
            child_check = await session.run(
                "MATCH (n:DialogueNode {node_id: $node_id}) RETURN n",
                node_id=child_node_id
            )
            if not await child_check.single():
                raise ValueError(f"子节点不存在: {child_node_id}")
            
            # 创建关系
            if fragment_id:
                await session.run(
                    """
                    MATCH (parent:DialogueNode {node_id: $parent_node_id}),
                          (child:DialogueNode {node_id: $child_node_id})
                    MERGE (parent)-[r:HAS_CHILD {fragment_id: $fragment_id}]->(child)
                    """,
                    parent_node_id=parent_node_id,
                    child_node_id=child_node_id,
                    fragment_id=fragment_id
                )
            else:
                await session.run(
                    """
                    MATCH (parent:DialogueNode {node_id: $parent_node_id}),
                          (child:DialogueNode {node_id: $child_node_id})
                    MERGE (parent)-[r:HAS_CHILD]->(child)
                    """,
                    parent_node_id=parent_node_id,
                    child_node_id=child_node_id
                )
    
    async def get_dialogue_node(
        self,
        node_id: str
    ) -> Optional[Dict]:
        """
        获取单个对话节点
        
        Args:
            node_id: 节点 ID
            
        Returns:
            节点信息字典，如果不存在则返回 None
        """
        async with self.driver.session() as session:
            result = await session.run(
                "MATCH (n:DialogueNode {node_id: $node_id}) RETURN n",
                node_id=node_id
            )
            record = await result.single()
            if record:
                node = dict(record["n"])
                return node
            return None
    
    async def get_dialogue_tree(
        self,
        root_node_id: str,
        user_id: str,
        max_depth: int = 10
    ) -> Optional[Dict]:
        """
        获取对话树（递归查询）
        
        Args:
            root_node_id: 根节点 ID
            user_id: 用户 ID（用于验证）
            max_depth: 最大深度
            
        Returns:
            对话树节点字典，如果不存在则返回 None
        """
        async with self.driver.session() as session:
            # 获取根节点
            root_result = await session.run(
                """
                MATCH (n:DialogueNode {node_id: $node_id, user_id: $user_id})
                RETURN n
                """,
                node_id=root_node_id,
                user_id=user_id
            )
            root_record = await root_result.single()
            if not root_record:
                return None
            
            root_node = dict(root_record["n"])
            # 确保 node_id 字段存在
            if "node_id" not in root_node:
                root_node["node_id"] = root_node_id
            
            # 递归获取子节点
            async def get_children(parent_id: str, depth: int) -> List[Dict]:
                if depth >= max_depth:
                    return []
                
                result = await session.run(
                    """
                    MATCH (parent:DialogueNode {node_id: $parent_id})-[:HAS_CHILD]->(child:DialogueNode)
                    RETURN child
                    ORDER BY child.timestamp
                    """,
                    parent_id=parent_id
                )
                
                children = []
                async for record in result:
                    child_node = dict(record["child"])
                    child_node_id = child_node.get("node_id")
                    if not child_node_id:
                        continue  # 跳过没有 node_id 的节点
                    
                    # 递归获取子节点的子节点
                    child_node["children"] = await get_children(child_node_id, depth + 1)
                    children.append(child_node)
                
                return children
            
            root_node["children"] = await get_children(root_node_id, 0)
            return root_node


# 全局客户端实例
neo4j_client = Neo4jClient()
