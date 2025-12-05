import React, { useState } from 'react';
import styles from './AskTheTextbookButton.module.css';

interface AskTheTextbookButtonProps {
  onOpenChat?: () => void;
}

export default function AskTheTextbookButton({ onOpenChat }: AskTheTextbookButtonProps): JSX.Element {
  const [isHovered, setIsHovered] = useState(false);

  const handleClick = () => {
    if (onOpenChat) {
      onOpenChat();
    }
  };

  return (
    <button
      className={styles.floatingButton}
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      aria-label="Ask the textbook a question"
      title="Ask the Textbook"
    >
      <span className={styles.icon}>💬</span>
      {isHovered && (
        <span className={styles.label}>Ask the Textbook</span>
      )}
    </button>
  );
}
