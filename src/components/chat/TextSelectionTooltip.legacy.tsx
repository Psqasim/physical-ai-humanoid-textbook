import React from 'react';
import styles from './TextSelectionTooltip.legacy.module.css';

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
}: TextSelectionTooltipProps): JSX.Element {
  if (!visible) {
    return null;
  }

  const handleClick = () => {
    if (onAskAbout && selectedText) {
      onAskAbout(selectedText);
    }
  };

  return (
    <div
      className={styles.tooltip}
      style={{
        top: `${position.top}px`,
        left: `${position.left}px`,
      }}
    >
      <button
        className={styles.tooltipButton}
        onClick={handleClick}
        aria-label="Ask about selected text"
      >
        <span className={styles.icon}>✨</span>
        <span className={styles.text}>Ask about this</span>
      </button>
    </div>
  );
}
