/**
 * DocItem Layout Theme Override - Clean production version
 *
 * This file extends the default DocItem layout.
 * Production version: Removed translation toggle for clean, minimal UI.
 */

import React from 'react';
import DocItemLayoutOriginal from '@theme-original/DocItem/Layout';
import type { Props } from '@theme/DocItem/Layout';

export default function DocItemLayout({ children }: Props): JSX.Element {
  // Clean production version - no language CTAs
  return <DocItemLayoutOriginal>{children}</DocItemLayoutOriginal>;
}
