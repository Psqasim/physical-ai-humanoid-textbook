import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Module 1 – ROS 2: Robotic Nervous System',
      collapsible: false,
      items: [
        'module-1-ros2/overview',
        'module-1-ros2/chapter-1-basics',
      ],
    },
    {
      type: 'category',
      label: 'Module 2 – Digital Twin (Gazebo & Unity)',
      collapsible: false,
      items: [
        'module-2-digital-twin-gazebo-unity/overview',
        'module-2-digital-twin-gazebo-unity/chapter-1-simulation-basics',
      ],
    },
    {
      type: 'category',
      label: 'Module 3 – NVIDIA Isaac (AI-Robot Brain)',
      collapsible: false,
      items: [
        'module-3-nvidia-isaac/overview',
        'module-3-nvidia-isaac/chapter-1-getting-started',
      ],
    },
    {
      type: 'category',
      label: 'Module 4 – Vision-Language-Action (VLA)',
      collapsible: false,
      items: [
        'module-4-vision-language-action/overview',
        'module-4-vision-language-action/chapter-1-vla-intro',
      ],
    },
  ],
};

export default sidebars;
