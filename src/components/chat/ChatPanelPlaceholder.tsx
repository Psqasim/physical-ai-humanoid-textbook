import React, { useState, useEffect } from 'react';
import styles from './ChatPanelPlaceholder.module.css';

interface ChatPanelPlaceholderProps {
  isOpen?: boolean;
  onClose?: () => void;
  selectedText?: string;
  initialMode?: 'whole-book' | 'selection';
}

type ChatMode = 'whole-book' | 'selection';

export default function ChatPanelPlaceholder({
  isOpen = false,
  onClose,
  selectedText = '',
  initialMode = 'whole-book'
}: ChatPanelPlaceholderProps): JSX.Element {
  const [mode, setMode] = useState<ChatMode>(initialMode);

  // Update mode when initialMode prop changes
  useEffect(() => {
    if (isOpen) {
      setMode(initialMode);
    }
  }, [isOpen, initialMode]);

  if (!isOpen) {
    return null;
  }

  return (
    <div className={styles.overlay}>
      <div className={styles.panel}>
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

        <div className={styles.content}>
          {mode === 'selection' && selectedText && (
            <div className={styles.selectedTextContext}>
              <h4 className={styles.contextTitle}>Selected Text:</h4>
              <div className={styles.contextText}>
                "{selectedText}"
              </div>
            </div>
          )}

          <div className={styles.statusBanner}>
            <div className={styles.statusIcon}>⚠️</div>
            <div className={styles.statusText}>
              <h3 className={styles.statusTitle}>Chatbot Backend Not Connected</h3>
              <p className={styles.statusDescription}>
                {mode === 'whole-book'
                  ? 'The AI-powered whole-book Q&A feature is not available yet. This will allow you to ask questions about any content in the textbook.'
                  : 'The selection-based Q&A feature is not available yet. This will allow you to select text and ask specific questions about it.'}
              </p>
            </div>
          </div>

          <div className={styles.placeholder}>
            <div className={styles.placeholderIcon}>💬</div>
            <p className={styles.placeholderText}>
              Coming soon: Ask questions and get instant answers powered by AI
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
