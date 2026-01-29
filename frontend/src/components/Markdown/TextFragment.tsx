import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css' 
import { ContentFragment } from '../../types/api'

/**
 * Markdown 文本片段组件
 * 为代码块和公式注入唯一 ID，支持划词选择
 */
interface TextFragmentProps {
  content: string
  fragments?: ContentFragment[]
  onFragmentSelect?: (fragmentId: string) => void
}

// 新增这个“翻译”函数，把 AI 的方括号变成 $ 符号
const preprocessLaTeX = (content: string) => {
  if (typeof content !== 'string') return ''
  return content
    .replace(/\\\[/g, '$$$') // 把 \[ 变成 $$
    .replace(/\\\]/g, '$$$') // 把 \] 变成 $$
    .replace(/\\\(/g, '$')   // 把 \( 变成 $
    .replace(/\\\)/g, '$')   // 把 \) 变成 $
}

const TextFragment: React.FC<TextFragmentProps> = ({
  content,
  fragments = [],
  onFragmentSelect,
}) => {
  /**
   * 处理文本选择事件
   */
  const handleSelection = () => {
    const selection = window.getSelection()
    if (!selection || selection.rangeCount === 0) return

    const selectedText = selection.toString().trim()
    if (!selectedText) return

    // 查找匹配的 fragment
    const matchedFragment = fragments.find((fragment) =>
      selectedText.includes(fragment.content) || fragment.content.includes(selectedText)
    )

    if (matchedFragment && onFragmentSelect) {
      onFragmentSelect(matchedFragment.id)
    }
  }

  return (
    <div
      onMouseUp={handleSelection}
      style={{
        lineHeight: '1.6',
        fontSize: '1rem',
      }}
    >
      <ReactMarkdown
        remarkPlugins={[remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          code: ({ node, className, children, ...props }) => {
            const codeString = String(children).replace(/\n$/, '')
            const fragment = fragments.find((f) => f.content === codeString && f.type === 'code')
            
            return (
              <code
                id={fragment?.id}
                className={className}
                style={{
                  backgroundColor: '#f4f4f4',
                  padding: '2px 4px',
                  borderRadius: '3px',
                  cursor: fragment ? 'pointer' : 'default',
                }}
                {...props}
              >
                {children}
              </code>
            )
          },
          pre: ({ children }) => {
            return (
              <pre
                style={{
                  backgroundColor: '#f4f4f4',
                  padding: '1rem',
                  borderRadius: '4px',
                  overflow: 'auto',
                }}
              >
                {children}
              </pre>
            )
          },
        }}
      >
        {/* 这里一定要用处理过的文本！ */}
        {preprocessLaTeX(content)}
      </ReactMarkdown>
    </div>
  )
}

export default TextFragment