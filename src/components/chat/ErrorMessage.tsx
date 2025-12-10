import React from 'react';
import styles from './ErrorMessage.module.css';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
}

/**
 * ErrorMessage Component
 *
 * Displays error messages with optional retry and dismiss actions.
 * Used in chat panel to show connection errors, API failures, etc.
 *
 * Features:
 * - Error icon (⚠️) for visual recognition
 * - Clear error message text
 * - Optional retry button (if onRetry provided)
 * - Optional dismiss button (if onDismiss provided)
 * - Red/warning color scheme
 * - Accessible with proper ARIA labels
 * - Theme-aware colors
 *
 * Phase: 2 (Component Extraction)
 * Feature: 003-chat-ui-redesign
 */
export default function ErrorMessage({ message, onRetry, onDismiss }: ErrorMessageProps): JSX.Element {
  return (
    <div className={styles.container} role="alert" aria-live="assertive">
      <div className={styles.icon}>⚠️</div>
      <div className={styles.content}>
        <p className={styles.message}>{message}</p>
        {(onRetry || onDismiss) && (
          <div className={styles.actions}>
            {onRetry && (
              <button
                onClick={onRetry}
                className={styles.retryButton}
                aria-label="Retry action"
              >
                🔄 Retry
              </button>
            )}
            {onDismiss && (
              <button
                onClick={onDismiss}
                className={styles.dismissButton}
                aria-label="Dismiss error message"
              >
                ✕ Dismiss
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
