import { marked } from 'marked'
import hljs from 'highlight.js'

// 配置marked
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value
      } catch (err) {
        console.error('Highlight error:', err)
      }
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true
})

export const parseMarkdown = (text: string): string => {
  if (!text) return ''
  
  try {
    return marked(text)
  } catch (error) {
    console.error('Markdown parsing error:', error)
    return text
  }
}

export const extractThinkingContent = (content: string): { thinking: string; reply: string } => {
  if (!content) return { thinking: '', reply: '' }
  
  // 支持多种思考内容格式
  const thinkingPatterns = [
    /```thinking\n([\s\S]*?)\n```/i,
    /```思考\n([\s\S]*?)\n```/i,
    /```thinking\s*\n([\s\S]*?)\n```/i,
    /```思考\s*\n([\s\S]*?)\n```/i,
    /<thinking>([\s\S]*?)<\/thinking>/i,
    /<思考>([\s\S]*?)<\/思考>/i,
    /<thinking>([\s\S]*?)<\/thinking>/gi,
    /<思考>([\s\S]*?)<\/思考>/gi
  ]
  
  for (const pattern of thinkingPatterns) {
    const match = content.match(pattern)
    if (match) {
      const thinking = match[1].trim()
      const reply = content.replace(match[0], '').trim()
      return { thinking, reply }
    }
  }
  
  // 如果没有找到思考内容，返回原始内容作为回复
  return { thinking: '', reply: content.trim() }
}

export const hasThinkingContent = (content: string): boolean => {
  // 检查是否包含思考内容标记
  const thinkingPatterns = [
    /```thinking/i,
    /```思考/i,
    /<thinking>/i,
    /<思考>/i
  ]
  
  return thinkingPatterns.some(pattern => pattern.test(content))
} 