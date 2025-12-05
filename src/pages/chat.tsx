import React, { useState } from 'react';
import Layout from '@theme/Layout';
import ChatPanelPlaceholder from '@site/src/components/chat/ChatPanelPlaceholder';
import styles from './chat.module.css';

export default function ChatPage(): JSX.Element {
  const [isPanelOpen, setIsPanelOpen] = useState(true);

  return (
    <Layout
      title="Study Assistant"
      description="AI-powered study assistant for the Physical AI Humanoid Textbook"
    >
      <main className={styles.chatPageMain}>
        <div className={styles.container}>
          <div className={styles.header}>
            <h1 className={styles.title}>Study Assistant</h1>
            <p className={styles.subtitle}>
              Ask questions about the textbook content and get instant AI-powered answers
            </p>
          </div>

          <div className={styles.features}>
            <div className={styles.feature}>
              <div className={styles.featureIcon}>📚</div>
              <h3 className={styles.featureTitle}>Whole-book Q&A</h3>
              <p className={styles.featureDescription}>
                Ask questions about any topic in the textbook and get comprehensive answers
                drawing from all chapters and modules.
              </p>
            </div>

            <div className={styles.feature}>
              <div className={styles.featureIcon}>✨</div>
              <h3 className={styles.featureTitle}>Selection-based Q&A</h3>
              <p className={styles.featureDescription}>
                Select specific text on any page and ask targeted questions about that content
                for deeper understanding.
              </p>
            </div>

            <div className={styles.feature}>
              <div className={styles.featureIcon}>🎯</div>
              <h3 className={styles.featureTitle}>Context-aware</h3>
              <p className={styles.featureDescription}>
                Get answers tailored to your learning level with awareness of previous questions
                and your progress through the course.
              </p>
            </div>
          </div>

          <div className={styles.cta}>
            <button
              className={styles.ctaButton}
              onClick={() => setIsPanelOpen(true)}
            >
              Open Study Assistant
            </button>
          </div>
        </div>
      </main>

      <ChatPanelPlaceholder
        isOpen={isPanelOpen}
        onClose={() => setIsPanelOpen(false)}
      />
    </Layout>
  );
}
