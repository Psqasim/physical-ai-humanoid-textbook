import React, { useState, useEffect, useRef } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './ChatPanelPlaceholder.legacy.module.css';

interface ChatPanelPlaceholderProps {
  isOpen?: boolean;
  onClose?: () => void;
  selectedText?: string;
  initialMode?: 'whole-book' | 'selection';
}

type ChatMode = 'whole-book' | 'selection';

interface Citation {
  docPath: string;
  heading: string;
  snippet: string;
}

interface Message {
  role: 'user' | 'assistant';
  text: string;
  citations?: Citation[];
}

interface ChatRequest {
  mode: string;
  question: string;
  selectedText?: string;
  docPath?: string;
  userId: string | null;
}

interface ChatResponse {
  answer: string;
  citations: Citation[];
  mode: string;
}

export default function ChatPanelPlaceholder({
  isOpen = false,
  onClose,
  selectedText = '',
  initialMode = 'whole-book'
}: ChatPanelPlaceholderProps): JSX.Element {
  const { siteConfig } = useDocusaurusContext();
  const backendUrl = (siteConfig.customFields?.backendUrl as string | undefined) ?? 'http://localhost:8001';
  const [mode, setMode] = useState<ChatMode>(initialMode);
  const [input, setInput] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // DEBUG: Log props on mount and when they change
  useEffect(() => {
    console.log('=== ChatPanel Props Updated ===');
    console.log('isOpen:', isOpen);
    console.log('selectedText:', selectedText);
    console.log('selectedText length:', selectedText?.length);
    console.log('initialMode:', initialMode);
    console.log('==============================');
  }, [isOpen, selectedText, initialMode]);

  // Update mode when initialMode prop changes
  // If initialMode is 'selection' but selectedText is empty, fallback to 'whole-book'
  useEffect(() => {
    if (isOpen) {
      if (initialMode === 'selection' && (!selectedText || !selectedText.trim())) {
        console.warn('Selection mode requested but no text selected. Falling back to whole-book mode.');
        setMode('whole-book');
      } else {
        setMode(initialMode);
      }
    }
  }, [isOpen, initialMode, selectedText]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Reset state when panel closes
  useEffect(() => {
    if (!isOpen) {
      setError(null);
    }
  }, [isOpen]);

  /**
   * Compute the doc path from current URL
   */
  const getDocPath = (): string => {
    const baseUrl = siteConfig.baseUrl || '/';
    let path = window.location.pathname;

    // Remove base URL prefix (e.g., /physical-ai-humanoid-textbook/)
    if (path.startsWith(baseUrl) && baseUrl !== '/') {
      path = path.substring(baseUrl.length);
    }

    // Ensure path starts with /
    if (!path.startsWith('/')) {
      path = '/' + path;
    }

    // CRITICAL: Ensure path starts with /docs/
    // If it already starts with /docs/, keep it
    // If it starts with something else, this is likely wrong
    if (!path.startsWith('/docs/')) {
      console.warn(`Unexpected docPath format: ${path}`);
      // Try to fix: if path is like "docs/module-1/...", prepend /
      if (path.startsWith('docs/')) {
        path = '/' + path;
      } else {
        // If path doesn't contain docs at all, something is very wrong
        console.error(`Cannot compute docPath from: ${window.location.pathname}`);
        return '/docs/intro'; // Fallback
      }
    }

    // Remove trailing slash (except for root /docs/)
    if (path.endsWith('/') && path !== '/docs/') {
      path = path.slice(0, -1);
    }

    // DEBUG: Log the computed path
    console.log('=== Doc Path Computation ===');
    console.log('window.location.pathname:', window.location.pathname);
    console.log('baseUrl:', baseUrl);
    console.log('Computed docPath:', path);
    console.log('===========================');

    return path;
  };

  /**
   * Build citation URL from docPath
   */
  const getCitationUrl = (docPath: string): string => {
    const baseUrl = siteConfig.baseUrl || '/';

    // Remove /docs prefix if present
    let cleanPath = docPath;
    if (cleanPath.startsWith('/docs/')) {
      cleanPath = cleanPath.substring(6); // Remove '/docs/'
    } else if (cleanPath.startsWith('docs/')) {
      cleanPath = cleanPath.substring(5); // Remove 'docs/'
    }

    // Build full URL
    return `${baseUrl}docs/${cleanPath}`.replace(/\/+/g, '/');
  };

  /**
   * Handle sending a message
   */
  const handleSend = async () => {
    if (!input.trim() || loading) {
      return;
    }

    // DEBUG: Log selection mode state
    console.log('=== DEBUG SELECTION MODE ===');
    console.log('mode:', mode);
    console.log('selectedText:', selectedText);
    console.log('selectedText length:', selectedText?.length);
    console.log('initialMode:', initialMode);
    console.log('===========================');

    const question = input.trim();

    // Validate selection mode has text
    if (mode === 'selection' && (!selectedText || !selectedText.trim())) {
      setError('Please select text first before asking a question in selection mode.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Build request payload
      const payload: ChatRequest = {
        mode,
        question,
        userId: null, // Anonymous for now
      };

      if (mode === 'selection') {
        payload.selectedText = selectedText || '';
        payload.docPath = getDocPath();
      }

      // DEBUG: Log payload before sending
      console.log('=== API Request Payload ===');
      console.log('Payload:', JSON.stringify(payload, null, 2));
      console.log('==========================');

      // Make API call
      const response = await fetch(`${backendUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        // Try to parse error message
        let errorMessage = 'The chatbot is temporarily unavailable. Please try again.';
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMessage = errorData.detail;
          }
        } catch (e) {
          // Use default error message
        }
        throw new Error(errorMessage);
      }

      const data: ChatResponse = await response.json();

      // Add user message
      const userMessage: Message = {
        role: 'user',
        text: question,
      };

      // Add assistant message
      const assistantMessage: Message = {
        role: 'assistant',
        text: data.answer,
        citations: data.citations,
      };

      setMessages(prev => [...prev, userMessage, assistantMessage]);
      setInput(''); // Clear input
    } catch (err) {
      console.error('Chat API error:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle Enter key press
   */
  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className={styles.overlay}>
      <div className={styles.panel}>
        {/* Header */}
        <div className={styles.header}>
          <h2 className={styles.title}>Study Assistant</h2>
          <button
            className={styles.closeButton}
            onClick={onClose}
            aria-label="Close chat panel"
          >
            ✕
          </button>
        </div>

        {/* Mode Selector */}
        <div className={styles.modeSelector}>
          <button
            className={`${styles.modeButton} ${mode === 'whole-book' ? styles.active : ''}`}
            onClick={() => setMode('whole-book')}
          >
            📚 Whole-book Q&A
          </button>
          <button
            className={`${styles.modeButton} ${mode === 'selection' ? styles.active : ''}`}
            onClick={() => setMode('selection')}
          >
            ✨ Selection-based Q&A
          </button>
        </div>

        {/* Content Area */}
        <div className={styles.content}>
          {/* Selected Text Preview (for selection mode) */}
          {mode === 'selection' && selectedText && (
            <div className={styles.selectedTextContext}>
              <h4 className={styles.contextTitle}>Selected Text:</h4>
              <div className={styles.contextText}>
                "{selectedText}"
              </div>
            </div>
          )}

          {/* Error Banner */}
          {error && (
            <div className={styles.errorBanner}>
              <div className={styles.errorIcon}>⚠️</div>
              <div className={styles.errorText}>{error}</div>
            </div>
          )}

          {/* Messages List */}
          <div className={styles.messagesList}>
            {messages.length === 0 && !loading && (
              <div className={styles.emptyState}>
                <div className={styles.emptyStateIcon}>💬</div>
                <p className={styles.emptyStateText}>
                  {mode === 'whole-book'
                    ? 'Ask any question about the textbook content'
                    : 'Ask a question about the selected text'}
                </p>
              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={`${styles.message} ${
                  message.role === 'user' ? styles.userMessage : styles.assistantMessage
                }`}
              >
                <div className={styles.messageRole}>
                  {message.role === 'user' ? '👤 You' : '🤖 Assistant'}
                </div>
                <div className={styles.messageText}>{message.text}</div>

                {/* Citations (for assistant messages) */}
                {message.role === 'assistant' && message.citations && message.citations.length > 0 && (
                  <div className={styles.citations}>
                    <div className={styles.citationsTitle}>📚 Sources:</div>
                    <ul className={styles.citationsList}>
                      {message.citations.map((citation, citIndex) => (
                        <li key={citIndex} className={styles.citationItem}>
                          <a
                            href={getCitationUrl(citation.docPath)}
                            className={styles.citationLink}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            <div className={styles.citationHeading}>
                              {citation.heading}
                            </div>
                            <div className={styles.citationSnippet}>
                              {citation.snippet}
                            </div>
                          </a>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}

            {/* Loading Indicator */}
            {loading && (
              <div className={styles.loadingMessage}>
                <div className={styles.loadingSpinner}>⏳</div>
                <div className={styles.loadingText}>Thinking...</div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className={styles.inputArea}>
          <textarea
            className={styles.input}
            placeholder={
              mode === 'whole-book'
                ? 'Ask a question about the textbook...'
                : 'Ask a question about the selected text...'
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
            rows={2}
          />
          <button
            className={styles.sendButton}
            onClick={handleSend}
            disabled={loading || !input.trim()}
            aria-label="Send message"
          >
            {loading ? '⏳' : '📤'} Send
          </button>
        </div>
      </div>
    </div>
  );
}
