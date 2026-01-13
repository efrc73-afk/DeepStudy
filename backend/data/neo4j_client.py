"""
Neo4j 知识图谱客户端
管理知识图谱的节点和关系
"""
from typing import List, Dict, Optional
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


# 全局客户端实例
neo4j_client = Neo4jClient()
