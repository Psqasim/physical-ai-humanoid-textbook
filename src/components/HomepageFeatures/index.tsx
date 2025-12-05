import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  emoji: string;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Physical AI & Embodied Intelligence',
    emoji: '🤖',
    description: (
      <>
        Dive into the world of embodied AI where intelligence meets the physical realm.
        Learn how robots perceive, reason, and act in real-world environments through
        advanced sensor fusion and decision-making systems.
      </>
    ),
  },
  {
    title: 'Digital Twin & Simulation',
    emoji: '🎮',
    description: (
      <>
        Master simulation-first development with Gazebo, Unity, and NVIDIA Isaac Sim.
        Build and test robots in photorealistic virtual environments before deploying
        to hardware, enabling rapid iteration and safe experimentation.
      </>
    ),
  },
  {
    title: 'Integrated AI Tutor',
    emoji: '💬',
    description: (
      <>
        Get personalized help as you learn with an AI-powered tutor (coming soon).
        Ask questions about any concept, get explanations tailored to your level,
        and receive instant feedback on your understanding.
      </>
    ),
  },
  {
    title: 'Adaptive Learning Paths',
    emoji: '📊',
    description: (
      <>
        Choose your journey: <strong>Beginner</strong> (fundamentals and guided projects),
        <strong>Intermediate</strong> (advanced topics and custom implementations), or
        <strong>Advanced</strong> (research papers and cutting-edge techniques).
        Content adapts to your skill level.
      </>
    ),
  },
];

function Feature({title, emoji, description}: FeatureItem) {
  return (
    <div className={clsx('col col--6')}>
      <div className={styles.featureCard}>
        <div className={styles.featureEmoji}>{emoji}</div>
        <div className="padding-horiz--md">
          <Heading as="h3">{title}</Heading>
          <p>{description}</p>
        </div>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
