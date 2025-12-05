import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          Physical AI & Humanoid Robotics
        </Heading>
        <p className="hero__subtitle">
          Master embodied intelligence and AI in the physical world. Learn to build intelligent robots through hands-on modules covering ROS 2, digital twins, NVIDIA Isaac, and vision-language-action models.
        </p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Start the Course
          </Link>
        </div>
      </div>
    </header>
  );
}

function AuthorSection() {
  return (
    <section className={styles.authorSection}>
      <div className="container">
        <div className={styles.authorContent}>
          <Heading as="h2" className={styles.authorTitle}>
            Authored by Muhammad Qasim
          </Heading>
          <p className={styles.authorDescription}>
            Passionate about robotics, AI, and embodied intelligence. Building the future of physical AI education.
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
            <Link
              className="button button--outline button--primary"
              href="mailto:muhammadqasim0326@gmail.com">
              Email
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Physical AI & Humanoid Robotics Textbook`}
      description="A comprehensive course on embodied intelligence, covering ROS 2, digital twins, NVIDIA Isaac, and vision-language-action models for robotics.">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <AuthorSection />
      </main>
    </Layout>
  );
}
