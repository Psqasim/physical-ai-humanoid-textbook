import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

/**
 * Language indicator strip showing supported languages
 */
function LanguageStrip() {
  return (
    <div className={styles.languageStrip} aria-label="Supported languages">
      <span className={styles.languageLabel}>Available in:</span>
      <span className={styles.languageTag}>EN</span>
      <span className={styles.languageTag}>اردو</span>
      <span className={styles.languageTag}>日本語</span>
    </div>
  );
}

/**
 * Voice mode badge
 */
function VoiceBadge() {
  return (
    <div className={styles.voiceBadge} aria-label="Voice input supported">
      <span className={styles.voiceIcon}>🎤</span>
      <span>Voice questions supported</span>
    </div>
  );
}

/**
 * Hero section with title, subtitle, language indicator, and CTA
 */
function HomepageHeader() {
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <LanguageStrip />
        <Heading as="h1" className="hero__title">
          Physical AI & Humanoid Robotics
        </Heading>
        <p className="hero__subtitle">
          Learn embodied intelligence, ROS 2, NVIDIA Isaac, and vision-language-action models.
        </p>
        <VoiceBadge />
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Start Learning
          </Link>
        </div>
      </div>
    </header>
  );
}

/**
 * Card data for the 4-card grid
 */
type CardItem = {
  title: string;
  description: string;
  icon: string;
  to: string;
  ariaLabel: string;
};

const CardList: CardItem[] = [
  {
    title: 'Course Textbook',
    description: 'Comprehensive modules covering ROS 2, digital twins, and AI-powered robotics.',
    icon: '📚',
    to: '/docs/intro',
    ariaLabel: 'Go to Course Textbook',
  },
  {
    title: 'Study Assistant',
    description: 'AI-powered chat with voice input. Ask questions in English, Urdu, or Japanese.',
    icon: '💬',
    to: '/chat',
    ariaLabel: 'Go to Study Assistant Chat',
  },
  {
    title: 'Multilingual Learning',
    description: 'Full content available in EN, اردو, and 日本語 with auto language detection.',
    icon: '🌐',
    to: '/docs/intro',
    ariaLabel: 'Start Multilingual Learning',
  },
  {
    title: 'How It Works',
    description: 'RAG-powered answers from textbook content with source citations.',
    icon: '⚡',
    to: '/chat',
    ariaLabel: 'Learn How RAG Works',
  },
];

/**
 * Single clickable card component
 */
function FeatureCard({title, description, icon, to, ariaLabel}: CardItem) {
  return (
    <Link to={to} className={styles.cardLink} aria-label={ariaLabel}>
      <article className={styles.card}>
        <div className={styles.cardIcon} aria-hidden="true">{icon}</div>
        <Heading as="h3" className={styles.cardTitle}>{title}</Heading>
        <p className={styles.cardDescription}>{description}</p>
      </article>
    </Link>
  );
}

/**
 * 4-card grid section
 */
function CardGrid() {
  return (
    <section className={styles.cardSection} aria-labelledby="features-heading">
      <div className="container">
        <Heading as="h2" id="features-heading" className="sr-only">
          Features
        </Heading>
        <div className={styles.cardGrid}>
          {CardList.map((card, idx) => (
            <FeatureCard key={idx} {...card} />
          ))}
        </div>
      </div>
    </section>
  );
}

/**
 * Author section
 */
function AuthorSection() {
  return (
    <section className={styles.authorSection}>
      <div className="container">
        <div className={styles.authorContent}>
          <Heading as="h2" className={styles.authorTitle}>
            Authored by Muhammad Qasim
          </Heading>
          <p className={styles.authorDescription}>
            Passionate about robotics, AI, and embodied intelligence.
          </p>
          <div className={styles.authorLinks}>
            <Link
              className="button button--outline button--primary"
              href="https://github.com/Psqasim"
              target="_blank"
              rel="noopener noreferrer">
              GitHub
            </Link>
            <Link
              className="button button--outline button--primary"
              href="https://www.linkedin.com/in/muhammad-qasim-5bba592b4/"
              target="_blank"
              rel="noopener noreferrer">
              LinkedIn
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

/**
 * Main homepage component
 */
export default function Home(): ReactNode {
  return (
    <Layout
      title="Physical AI & Humanoid Robotics Textbook"
      description="Learn embodied intelligence, ROS 2, digital twins, and vision-language-action models. AI-powered study assistant with voice input in English, Urdu, and Japanese.">
      <HomepageHeader />
      <main>
        <CardGrid />
        <AuthorSection />
      </main>
    </Layout>
  );
}
