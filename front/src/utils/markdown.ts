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
  const thinkingMatch = content.match(/```thinking\n([\s\S]*?)\n```/i) || 
                       content.match(/```思考\n([\s\S]*?)\n```/i)
  
  if (thinkingMatch) {
    const thinking = thinkingMatch[1].trim()
    const reply = content.replace(thinkingMatch[0], '').trim()
    return { thinking, reply }
  }
  
  return { thinking: '', reply: content.trim() }
}

export const hasThinkingContent = (content: string): boolean => {
  return content.includes('```thinking') || content.includes('```思考')
} 