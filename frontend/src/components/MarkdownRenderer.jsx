import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

/**
 * MarkdownRenderer - Converts Markdown to styled HTML
 * 
 * Handles:
 * - Bold text (**text**)
 * - SQL code blocks (```sql ... ```)
 * - Markdown tables (| col | col |)
 * - Emoji indicators (⚡, 🔍, 🔄)
 * - Italic text for attempt markers (_(Attempt 1/3)_)
 * 
 * Props:
 * - content: Raw Markdown string from backend
 */
function MarkdownRenderer({ content }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        // Custom code block rendering with SQL highlighting class
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '');
          const language = match ? match[1] : '';
          
          if (!inline && language) {
            return (
              <div className="code-block-wrapper">
                <div className="code-block-header">
                  <span className="code-language">{language.toUpperCase()}</span>
                </div>
                <pre className={`code-block language-${language}`}>
                  <code {...props}>{children}</code>
                </pre>
              </div>
            );
          }
          
          // Inline code
          return (
            <code className="inline-code" {...props}>
              {children}
            </code>
          );
        },
        // Tables with proper styling
        table({ children }) {
          return (
            <div className="table-wrapper">
              <table>{children}</table>
            </div>
          );
        },
        // Preserve line breaks in paragraphs
        p({ children }) {
          return <p>{children}</p>;
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

export default MarkdownRenderer;
