import logging
from typing import List, Dict, Optional
from neo4j import AsyncGraphDatabase
from neo4j.exceptions import (
    ServiceUnavailable, 
    AuthError, 
    ConstraintError,
    Neo4jError
)
from backend.config import settings

# 配置日志
logger = logging.getLogger("neo4j_client")
logging.basicConfig(level=logging.INFO)

class Neo4jClient:
    """Neo4j 客户端（带异常处理版）"""
    
    def __init__(self):
        """初始化 Neo4j 客户端并建立连接池"""
        self._uri = settings.NEO4J_URI
        self._user = settings.NEO4J_USER
        self._password = settings.NEO4J_PASSWORD
        self.driver = None

        try:
            self.driver = AsyncGraphDatabase.driver(
                self._uri,
                auth=(self._user, self._password)
            )
            logger.info(f"Neo4j driver initialized at {self._uri}")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j driver: {e}")
            raise e

    async def verify_connectivity(self):
        """验证数据库连接是否可用"""
        try:
            await self.driver.verify_connectivity()
            logger.info("Neo4j connection verified successfully.")
        except (ServiceUnavailable, AuthError) as e:
            logger.error(f"Neo4j connection verification failed: {e}")
            # 可以在这里抛出自定义异常，通知上层应用数据库不可用
            raise

    async def close(self):
        """关闭连接"""
        if self.driver:
            await self.driver.close()
            logger.info("Neo4j driver closed.")
    
    async def create_node(
        self,
        label: str,
        properties: Dict
    ) -> Optional[str]:
        """
        创建节点（处理唯一性约束冲突）
        """
        query = f"CREATE (n:{label} $properties) RETURN id(n) as node_id"
        
        try:
            async with self.driver.session() as session:
                result = await session.run(query, properties=properties)
                record = await result.single()
                node_id = str(record["node_id"])
                logger.debug(f"Created node [{label}] with ID: {node_id}")
                return node_id
                
        except ConstraintError as e:
            # 当违反唯一性约束时（例如用户名重复）
            logger.warning(f"Constraint violated while creating node {label}: {e}")
            return None  # 或者 raise 此异常，取决于业务逻辑
            
        except Exception as e:
            logger.error(f"Error creating node {label}: {e}")
            raise  # 其他未知错误继续向上抛出

    async def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: Optional[Dict] = None
    ) -> bool:
        """
        创建关系（增加返回值表示成功/失败）
        """
        query = f"""
            MATCH (a), (b)
            WHERE id(a) = $source_id AND id(b) = $target_id
            CREATE (a)-[r:{relation_type}]->(b)
        """
        if properties:
            query = f"""
            MATCH (a), (b)
            WHERE id(a) = $source_id AND id(b) = $target_id
            CREATE (a)-[r:{relation_type} $properties]->(b)
            """

        try:
            async with self.driver.session() as session:
                # 检查 source_id 和 target_id 是否为有效数字
                if not (source_id.isdigit() and target_id.isdigit()):
                     logger.error(f"Invalid ID format: {source_id}, {target_id}")
                     return False

                result = await session.run(
                    query,
                    source_id=int(source_id),
                    target_id=int(target_id),
                    properties=properties or {}
                )
                # 获取执行摘要以确认是否有关系被创建
                summary = await result.consume()
                if summary.counters.relationships_created > 0:
                    logger.debug(f"Created relationship {relation_type} between {source_id} and {target_id}")
                    return True
                else:
                    logger.warning(f"Failed to create relationship: Nodes {source_id} or {target_id} not found.")
                    return False
                    
        except Exception as e:
            logger.error(f"Error creating relationship: {e}")
            return False

    async def get_node_by_name(
        self,
        label: str,
        name: str
    ) -> Optional[Dict]:
        """根据名称获取节点"""
        query = f"MATCH (n:{label} {{name: $name}}) RETURN n, id(n) as node_id"
        
        try:
            async with self.driver.session() as session:
                result = await session.run(query, name=name)
                record = await result.single()
                
                if record:
                    node = dict(record["n"])
                    node["id"] = str(record["node_id"])
                    return node
                else:
                    logger.debug(f"Node not found: {label} {{name: {name}}}")
                    return None
                    
        except ServiceUnavailable as e:
            logger.critical(f"Database unavailable during get_node_by_name: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_node_by_name: {e}")
            return None

    async def get_related_nodes(
        self,
        node_id: str,
        relation_type: Optional[str] = None
    ) -> List[Dict]:
        """获取相关节点"""
        try:
            async with self.driver.session() as session:
                if not node_id.isdigit():
                    logger.warning(f"Invalid node_id: {node_id}")
                    return []

                if relation_type:
                    query = f"""
                    MATCH (a)-[r:{relation_type}]->(b)
                    WHERE id(a) = $node_id
                    RETURN b, id(b) as node_id, type(r) as relation
                    """
                else:
                    query = """
                    MATCH (a)-[r]->(b)
                    WHERE id(a) = $node_id
                    RETURN b, id(b) as node_id, type(r) as relation
                    """
                
                result = await session.run(query, node_id=int(node_id))
                records = await result.values()
                
                nodes = []
                for record in records:
                    node = dict(record[0])
                    node["id"] = str(record[1])
                    node["relation"] = record[2]
                    nodes.append(node)
                return nodes
                
        except Exception as e:
            logger.error(f"Error getting related nodes for {node_id}: {e}")
            return []
        
    async def get_learning_path(
        self,
        target_concept_name: str
    ) -> List[str]:
        """
        核心功能：查找从基础到目标概念的学习路径
        """
        # 这句 Cypher 的意思是：
        # 找到一个叫 target_concept_name 的节点
        # 然后往回找（<-[:REQUIRES*]-），直到找到没有依赖的根节点
        # path 就是这条路
        query = """
        MATCH (target:Concept {name: $name})
        MATCH path = (root)-[:REQUIRES|PART_OF*]->(target)
        RETURN [node in nodes(path) | node.name] AS steps
        ORDER BY length(path) DESC
        LIMIT 1
        """
        
        try:
            async with self.driver.session() as session:
                result = await session.run(query, name=target_concept_name)
                record = await result.single()
                
                if record:
                    # record["steps"] 就是数据库返回的列表
                    path = record["steps"]
                    logger.info(f"Found learning path for {target_concept_name}: {path}")
                    return path
                else:
                    logger.warning(f"No path found for {target_concept_name}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error finding learning path: {e}")
            return []

# 全局客户端实例
neo4j_client = Neo4jClient()
