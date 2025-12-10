/**
 * Feature Flags for Chat UI Components
 *
 * This file controls which version of the chat UI is loaded.
 *
 * Purpose:
 * - Provides instant rollback mechanism without redeployment
 * - Allows safe testing of new UI while preserving old UI
 * - Can be toggled for gradual rollout or A/B testing
 *
 * Usage:
 * - Set `enableNewChatUI` to `true` to use the redesigned chat UI
 * - Set `enableNewChatUI` to `false` to use the legacy (original) chat UI
 *
 * Rollback Strategy:
 * - If critical issues are found in new UI, toggle this flag to `false`
 * - No code changes or redeployment needed for rollback
 * - Legacy files (*.legacy.tsx, *.legacy.module.css) remain available for 1 sprint
 *
 * Feature: 003-chat-ui-redesign
 * Created: 2025-12-08
 */

/**
 * Enable the new redesigned chat UI (Phase 1-7 implementation)
 *
 * - `false`: Use legacy UI (ChatPanelPlaceholder.legacy.tsx, TextSelectionTooltip.legacy.tsx)
 * - `true` (default): Use new responsive, theme-aware UI (ChatPanelPlaceholder.tsx, TextSelectionTooltip.tsx)
 *
 * Updated: 2025-12-10 - Phase 7 complete, new UI enabled by default
 */
export const enableNewChatUI = true;
