// generated-fix: replaced internal imports with wrapper to avoid version-mismatch crashes
// generated-by: speckit-architect
/**
 * DocItem Theme Override - Safe Wrapper
 *
 * This file overrides the default Docusaurus DocItem component by wrapping
 * the original component. This approach avoids using internal APIs that may
 * not be available in all Docusaurus versions.
 *
 * The wrapper simply passes all props through to the original component,
 * ensuring compatibility while maintaining the ability to extend functionality.
 */

import React from 'react';
import DocItemOriginal from '@theme-original/DocItem';
import type { Props } from '@theme/DocItem';

export default function DocItem(props: Props): JSX.Element {
  // Safe fallback: if props are missing, render original component unmodified
  if (!props || !props.content) {
    return <DocItemOriginal {...props} />;
  }

  // Render the original DocItem component with all props
  // The Layout component will handle TranslationToggle integration
  return <DocItemOriginal {...props} />;
}
