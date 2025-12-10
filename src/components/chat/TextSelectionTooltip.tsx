import React, { useState, useEffect } from 'react';
import styles from './TextSelectionTooltip.module.css';

interface TextSelectionTooltipProps {
  position?: { top: number; left: number };
  selectedText?: string;
  onAskAbout?: (text: string) => void;
  visible?: boolean;
}

export default function TextSelectionTooltip({
  position = { top: 0, left: 0 },
  selectedText = '',
  onAskAbout,
  visible = false,
}: TextSelectionTooltipProps): JSX.Element | null {
  const [placement, setPlacement] = useState<'above' | 'below'>('above');

  // Smart positioning: if near top of viewport, show below; otherwise show above
  useEffect(() => {
    if (visible && position.top < 100) {
      setPlacement('below');
    } else {
      setPlacement('above');
    }
  }, [visible, position.top]);

  if (!visible) {
    return null;
  }

  const handleClick = () => {
    if (onAskAbout && selectedText) {
      onAskAbout(selectedText);
    }
  };

  // Preview text: first 50 chars with ellipsis if longer
  const previewText = selectedText.length > 50
    ? `${selectedText.substring(0, 50)}...`
    : selectedText;

  return (
    <div
      className={`${styles.tooltip} ${styles[placement]}`}
      style={{
        top: `${position.top}px`,
        left: `${position.left}px`,
      }}
      onClick={(e) => e.stopPropagation()}
    >
      <div className={styles.preview}>"{previewText}"</div>
      <button
        className={styles.tooltipButton}
        onClick={handleClick}
        aria-label="Ask about selected text"
        type="button"
      >
        <span className={styles.icon}>💬</span>
        <span className={styles.text}>Ask about this</span>
      </button>
    </div>
  );
}
