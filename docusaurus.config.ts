import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Physical AI & Humanoid Robotics Textbook',
  tagline: 'Master embodied intelligence and AI in the physical world',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true,
  },

  // Set the production url of your site here
  url: 'https://psqasim.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/physical-ai-humanoid-textbook/',
  deploymentBranch: 'gh-pages', 

  // GitHub pages deployment config.
  organizationName: 'Psqasim',
  projectName: 'physical-ai-humanoid-textbook',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Add trailing slash configuration for consistent routing
  trailingSlash: false,

  // i18n configuration for multilingual support
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ja', 'ur'],
    localeConfigs: {
      en: {
        label: 'English',
        direction: 'ltr',
        htmlLang: 'en-US',
      },
      ja: {
        label: '日本語',
        direction: 'ltr',
        htmlLang: 'ja-JP',
      },
      ur: {
        label: 'اردو',
        direction: 'rtl',
        htmlLang: 'ur-PK',
      },
    },
  },

  customFields: {
    backendUrl: process.env.DOCUSAURUS_BACKEND_URL ?? 'https://physical-ai-humanoid-textbook-production.up.railway.app',
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: 'docs',
        },
        blog: false, // Disable blog (per FR-012)
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Physical AI & Humanoid Robotics',
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Course',
        },
        {
          to: '/chat',
          label: 'Study Assistant',
          position: 'left',
        },
        {
          href: 'https://github.com/Psqasim',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Learn',
          items: [
            {
              label: 'Start Course',
              to: '/docs/intro',
            },
          ],
        },
        {
          title: 'Connect',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/Psqasim',
            },
            {
              label: 'LinkedIn',
              href: 'https://linkedin.com/in/muhammad-qasim',
            },
            {
              label: 'Email',
              href: 'mailto:muhammadqasim0326@gmail.com',
            },
          ],
        },
        {
          title: 'Legal',
          items: [
            {
              label: 'Terms & Conditions',
              to: '/terms',
            },
            {
              label: 'Privacy Policy',
              to: '/privacy',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Muhammad Qasim. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
