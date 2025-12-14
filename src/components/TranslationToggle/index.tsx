/**
 * TranslationToggle Component
 *
 * Displays available language translations for documentation pages
 * and shows translation completion percentage.
 *
 * Features:
 * - Reads translationMetadata from document frontmatter
 * - Displays language toggle buttons (EN | UR | JA)
 * - Shows completion badge for incomplete translations
 * - Switches between available language versions
 *
 * Usage:
 *   <TranslationToggle metadata={doc.frontMatter.translationMetadata} />
 */

import React from 'react';
import Link from '@docusaurus/Link';
import { useLocation } from '@docusaurus/router';
import { useDoc } from '@docusaurus/theme-common/internal';
import styles from './styles.module.css';

/**
 * Translation metadata structure from document frontmatter
 */
export interface TranslationMetadata {
  sourceLanguage: 'en' | 'ur' | 'ja';
  availableLanguages: Array<'en' | 'ur' | 'ja'>;
  completionPercentage?: {
    en?: number;
    ur?: number;
    ja?: number;
  };
  lastUpdated?: {
    en?: string;
    ur?: string;
    ja?: string;
  };
}

/**
 * Language display configuration
 */
const LANGUAGE_CONFIG = {
  en: {
    code: 'en',
    label: 'EN',
    fullName: 'English',
  },
  ur: {
    code: 'ur',
    label: 'UR',
    fullName: 'اردو',
  },
  ja: {
    code: 'ja',
    label: 'JA',
    fullName: '日本語',
  },
};

interface TranslationToggleProps {
  metadata?: TranslationMetadata;
}

/**
 * CompletionBadge displays translation completion percentage
 */
function CompletionBadge({ percentage }: { percentage: number }) {
  if (percentage >= 100) {
    return null;
  }

  // Determine badge color based on completion
  const badgeClass =
    percentage >= 80
      ? styles.badgeHigh
      : percentage >= 50
      ? styles.badgeMedium
      : styles.badgeLow;

  return (
    <span className={`${styles.completionBadge} ${badgeClass}`}>
      {percentage}% complete
    </span>
  );
}

/**
 * Extract current language code from URL path
 */
function getCurrentLanguage(pathname: string): 'en' | 'ur' | 'ja' {
  // Check if path starts with language code (e.g., /ur/docs/...)
  if (pathname.startsWith('/ur/')) {
    return 'ur';
  }
  if (pathname.startsWith('/ja/')) {
    return 'ja';
  }
  // Default to English
  return 'en';
}

/**
 * Build translation URL for a given language
 */
function getTranslationUrl(
  currentPath: string,
  currentLang: 'en' | 'ur' | 'ja',
  targetLang: 'en' | 'ur' | 'ja'
): string {
  // If switching to English, remove language prefix
  if (targetLang === 'en') {
    if (currentLang === 'en') {
      return currentPath;
    }
    // Remove /ur/ or /ja/ prefix
    return currentPath.replace(`/${currentLang}/`, '/');
  }

  // If switching from English to another language, add prefix
  if (currentLang === 'en') {
    return `/${targetLang}${currentPath}`;
  }

  // If switching between non-English languages, replace prefix
  return currentPath.replace(`/${currentLang}/`, `/${targetLang}/`);
}

/**
 * TranslationToggle Component
 *
 * Displays available translations and allows switching between languages
 */
export default function TranslationToggle({
  metadata,
}: TranslationToggleProps): JSX.Element | null {
  const location = useLocation();
  const currentLang = getCurrentLanguage(location.pathname);

  // If no metadata provided, don't show toggle
  if (!metadata || !metadata.availableLanguages) {
    return null;
  }

  const { availableLanguages, completionPercentage } = metadata;

  // If only one language available, don't show toggle
  if (availableLanguages.length <= 1) {
    return null;
  }

  return (
    <div className={styles.translationToggle}>
      <div className={styles.toggleLabel}>
        <span className={styles.labelIcon}>🌐</span>
        <span className={styles.labelText}>Available in:</span>
      </div>

      <div className={styles.languageButtons}>
        {availableLanguages.map((lang) => {
          const config = LANGUAGE_CONFIG[lang];
          const isActive = currentLang === lang;
          const completion = completionPercentage?.[lang] ?? 100;
          const translationUrl = getTranslationUrl(
            location.pathname,
            currentLang,
            lang
          );

          return (
            <div key={lang} className={styles.languageButtonWrapper}>
              {isActive ? (
                <span
                  className={`${styles.languageButton} ${styles.languageButtonActive}`}
                  title={config.fullName}
                >
                  {config.label}
                </span>
              ) : (
                <Link
                  to={translationUrl}
                  className={styles.languageButton}
                  title={`Switch to ${config.fullName}`}
                >
                  {config.label}
                </Link>
              )}

              {completion < 100 && (
                <div className={styles.completionBadgeWrapper}>
                  <CompletionBadge percentage={completion} />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Optional: Last updated info */}
      {metadata.lastUpdated && metadata.lastUpdated[currentLang] && (
        <div className={styles.lastUpdated}>
          Last updated: {new Date(metadata.lastUpdated[currentLang]!).toLocaleDateString()}
        </div>
      )}
    </div>
  );
}
