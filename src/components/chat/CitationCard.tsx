import React from 'react';
import styles from './CitationCard.module.css';

interface CitationCardProps {
  citation: {
    docPath: string;
    heading: string;
    snippet: string;
  };
  baseUrl?: string;
}

/**
 * CitationCard Component
 *
 * Displays a citation as a clickable card with icon, heading, and snippet preview.
 * Used in chat messages to show source references from the RAG system.
 *
 * Features:
 * - Document icon (📄) for visual recognition
 * - Clickable card that navigates to the cited document
 * - Hover effect: border color changes to primary blue
 * - Responsive text sizing for mobile/desktop
 * - Truncated heading (ellipsis if too long)
 * - Snippet clamped to 2 lines with line-clamp
 *
 * Phase: 2 (Component Extraction)
 * Feature: 003-chat-ui-redesign
 */
export default function CitationCard({ citation, baseUrl = '/' }: CitationCardProps): JSX.Element {
  /**
   * Build full URL from docPath
   * Cleans the path and constructs proper URL for navigation
   */
  const getCitationUrl = (docPath: string): string => {
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

  return (
    <a
      href={getCitationUrl(citation.docPath)}
      className={styles.card}
      target="_blank"
      rel="noopener noreferrer"
      aria-label={`Citation: ${citation.heading}`}
    >
      <div className={styles.icon}>📄</div>
      <div className={styles.content}>
        <h5 className={styles.heading}>{citation.heading}</h5>
        <p className={styles.snippet}>{citation.snippet}</p>
      </div>
      <div className={styles.arrow}>→</div>
    </a>
  );
}
