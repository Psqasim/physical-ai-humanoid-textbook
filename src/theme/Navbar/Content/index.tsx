import React from 'react';
import Content from '@theme-original/Navbar/Content';
import type { Props } from '@theme/Navbar/Content';
import CustomLocaleSwitcher from '../CustomLocaleSwitcher';

/**
 * Navbar Content wrapper - Adds custom locale switcher to navbar items
 */
export default function ContentWrapper(props: Props): JSX.Element {
  return (
    <>
      <Content {...props} />
      {/* Add custom locale switcher */}
      <CustomLocaleSwitcher />
    </>
  );
}
