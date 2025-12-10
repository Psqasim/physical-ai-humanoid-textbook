import React from 'react';
import styles from './LoadingIndicator.module.css';

interface LoadingIndicatorProps {
  message?: string;
}

/**
 * LoadingIndicator Component
 *
 * Displays an animated loading indicator with 3 bouncing dots.
 * Used in chat messages while waiting for AI response.
 *
 * Features:
 * - 3 animated dots with staggered bounce effect
 * - Customizable loading message (default: "AI is thinking...")
 * - Centered layout within message area
 * - Theme-aware colors
 * - Smooth animations with GPU acceleration
 *
 * Phase: 2 (Component Extraction)
 * Feature: 003-chat-ui-redesign
 */
export default function LoadingIndicator({ message = 'AI is thinking...' }: LoadingIndicatorProps): JSX.Element {
  return (
    <div className={styles.container}>
      <div className={styles.dots}>
        <span className={styles.dot}></span>
        <span className={styles.dot}></span>
        <span className={styles.dot}></span>
      </div>
      {message && <p className={styles.message}>{message}</p>}
    </div>
  );
}
