import { useCallback, useMemo } from 'react'
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { MindMapGraph } from '../../types/api'
import { KnowledgeNode, KnowledgeEdge } from '../../types/reactflow'

/**
 * 知识图谱组件
 * 使用 ReactFlow 渲染思维导图
 */
interface KnowledgeGraphProps {
  data: MindMapGraph
  onNodeClick?: (nodeId: string) => void
}

const KnowledgeGraph: React.FC<KnowledgeGraphProps> = ({ data, onNodeClick }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState(data.nodes as Node[])
  const [edges, setEdges, onEdgesChange] = useEdgesState(data.edges as Edge[])

  /**
   * 处理节点连接
   */
  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  /**
   * 处理节点点击
   */
  const handleNodeClick = useCallback(
    (event: React.MouseEvent, node: Node) => {
      if (onNodeClick) {
        onNodeClick(node.id)
      }
    },
    [onNodeClick]
  )

  /**
   * 节点样式
   */
  const nodeTypes = useMemo(
    () => ({
      default: {
        style: {
          background: '#fff',
          border: '2px solid #007bff',
          borderRadius: '8px',
          padding: '10px',
          minWidth: '150px',
        },
      },
    }),
    []
  )

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  )
}

export default KnowledgeGraph
