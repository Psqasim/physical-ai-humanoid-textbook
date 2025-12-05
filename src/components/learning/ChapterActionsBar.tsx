import React, { useState } from 'react';
import styles from './ChapterActionsBar.module.css';

export interface ChapterActionsBarProps {
  chapterTitle: string;
}

export default function ChapterActionsBar({ chapterTitle }: ChapterActionsBarProps): React.ReactElement {
  const [personalizeAlert, setPersonalizeAlert] = useState(false);
  const [urduAlert, setUrduAlert] = useState(false);

  const handlePersonalizeClick = () => {
    setPersonalizeAlert(true);
    setTimeout(() => setPersonalizeAlert(false), 5000);
  };

  const handleUrduClick = () => {
    setUrduAlert(true);
    setTimeout(() => setUrduAlert(false), 5000);
  };

  return (
    <div className={styles.chapterActionsBar}>
      <div className={styles.buttonGroup}>
        <button
          className={styles.actionButton}
          onClick={handlePersonalizeClick}
          aria-label="Personalize this chapter for your skill level">
          Personalize for Me
        </button>
        <button
          className={styles.actionButton}
          onClick={handleUrduClick}
          aria-label="View this chapter in Urdu">
          View in Urdu
        </button>
      </div>

      {personalizeAlert && (
        <div className={styles.alert} role="alert">
          Personalization coming soon! This feature will adapt the content to your skill level (Beginner, Intermediate, or Advanced).
        </div>
      )}

      {urduAlert && (
        <div className={styles.alert} role="alert">
          Urdu translation coming soon! This feature will provide the full chapter content in Urdu.
        </div>
      )}
    </div>
  );
}
