import React from 'react';
import { useLocation } from '@docusaurus/router';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './styles.module.css';

/**
 * Custom Locale Switcher - Replaces broken Docusaurus localeDropdown
 *
 * This component properly handles locale switching by:
 * 1. Detecting current locale from URL
 * 2. Stripping it before adding new locale
 * 3. Constructing correct URLs
 */
export default function CustomLocaleSwitcher(): JSX.Element {
  const { i18n, siteConfig } = useDocusaurusContext();
  const location = useLocation();
  const { defaultLocale, locales } = i18n;

  // Known project name in the URL - this is the key identifier
  const PROJECT_NAME = 'physical-ai-humanoid-textbook';

  const handleLocaleChange = (newLocale: string) => {
    const pathname = location.pathname;

    // ROBUST PARSING: Find the project name in the URL and extract everything after it
    const projectIndex = pathname.indexOf(PROJECT_NAME);

    if (projectIndex === -1) {
      // Fallback: just go to root with new locale
      const newUrl = newLocale === defaultLocale
        ? `/${PROJECT_NAME}/`
        : `/${PROJECT_NAME}/${newLocale}/`;
      window.location.href = newUrl;
      return;
    }

    // Get the base path (everything up to and including project name)
    const basePath = pathname.substring(0, projectIndex + PROJECT_NAME.length);

    // Get everything after the project name
    let afterProject = pathname.substring(projectIndex + PROJECT_NAME.length);

    // Remove leading slash
    if (afterProject.startsWith('/')) {
      afterProject = afterProject.substring(1);
    }

    // Parse actual current locale from URL
    let actualCurrentLocale = defaultLocale;
    let contentPath = afterProject;

    // Check if path starts with any non-default locale
    for (const locale of locales) {
      if (locale !== defaultLocale) {
        if (afterProject === locale) {
          actualCurrentLocale = locale;
          contentPath = '';
          break;
        } else if (afterProject.startsWith(locale + '/')) {
          actualCurrentLocale = locale;
          contentPath = afterProject.substring(locale.length + 1);
          break;
        }
      }
    }

    // Skip if already on this locale
    if (newLocale === actualCurrentLocale) {
      return;
    }

    // Build the new URL
    let newUrl = basePath;

    // Add new locale prefix for non-default locales
    if (newLocale !== defaultLocale) {
      newUrl += '/' + newLocale;
    }

    // Add the content path
    if (contentPath) {
      newUrl += '/' + contentPath;
    } else {
      newUrl += '/';
    }

    // Navigate to the new URL
    window.location.href = newUrl + location.search + location.hash;
  };

  const localeLabels: Record<string, string> = {
    en: 'English',
    ja: '日本語',
    ur: 'اردو',
  };

  // Get the ACTUAL current locale from URL (not from context which may be stale)
  const getActualLocale = (): string => {
    const pathname = location.pathname;
    const projectIndex = pathname.indexOf(PROJECT_NAME);

    if (projectIndex === -1) return defaultLocale;

    let afterProject = pathname.substring(projectIndex + PROJECT_NAME.length);
    if (afterProject.startsWith('/')) {
      afterProject = afterProject.substring(1);
    }

    for (const locale of locales) {
      if (locale !== defaultLocale) {
        if (afterProject === locale || afterProject.startsWith(locale + '/')) {
          return locale;
        }
      }
    }
    return defaultLocale;
  };

  const actualLocale = getActualLocale();

  return (
    <div className={styles.localeSwitcher}>
      <select
        className={styles.localeDropdown}
        value={actualLocale}
        onChange={(e) => handleLocaleChange(e.target.value)}
        aria-label="Select language"
      >
        {locales.map((locale) => (
          <option key={locale} value={locale}>
            {localeLabels[locale] || locale}
          </option>
        ))}
      </select>
    </div>
  );
}
