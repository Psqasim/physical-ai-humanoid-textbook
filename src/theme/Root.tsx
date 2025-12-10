import React, { useState, useEffect } from 'react';
import AskTheTextbookButton from '@site/src/components/chat/AskTheTextbookButton';
import { enableNewChatUI } from '@site/src/components/chat/featureFlags';

// Chat components - Using new redesigned UI (003-chat-ui-redesign)
import ChatPanelPlaceholder from '@site/src/components/chat/ChatPanelPlaceholder';
import TextSelectionTooltip from '@site/src/components/chat/TextSelectionTooltip';

// Legacy components (preserved for reference):
// import ChatPanelPlaceholder from '@site/src/components/chat/ChatPanelPlaceholder.legacy';
// import TextSelectionTooltip from '@site/src/components/chat/TextSelectionTooltip.legacy';

const MIN_SELECTION_LENGTH = 10;

export default function Root({ children }: { children: React.ReactNode }): JSX.Element {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [preservedSelectedText, setPreservedSelectedText] = useState(''); // Preserve text when chat opens
  const [tooltipVisible, setTooltipVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });
  const [initialChatMode, setInitialChatMode] = useState<'whole-book' | 'selection'>('whole-book');

  useEffect(() => {
    const handleSelection = () => {
      // CRITICAL: Don't update selectedText when chat is open
      // This prevents the text from being cleared when chat UI elements get selected
      if (isChatOpen) {
        console.log('=== Text Selection Ignored (Chat Open) ===');
        return;
      }

      const selection = window.getSelection();
      if (!selection) return;

      const text = selection.toString().trim();

      if (text.length >= MIN_SELECTION_LENGTH) {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        // Position tooltip above and centered on the selection
        const top = rect.top + window.scrollY - 50; // 50px above selection
        const left = rect.left + window.scrollX + rect.width / 2 - 75; // Center tooltip (assuming ~150px width)

        console.log('=== Text Selection Detected ===');
        console.log('Selected text:', text);
        console.log('Text length:', text.length);
        console.log('===============================');

        setSelectedText(text);
        setTooltipPosition({ top, left });
        setTooltipVisible(true);
      } else {
        setTooltipVisible(false);
        setSelectedText('');
      }
    };

    const handleMouseUp = () => {
      // Small delay to ensure selection is complete
      setTimeout(handleSelection, 10);
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      // Only handle selection-related keys
      if (e.shiftKey || e.key === 'ArrowLeft' || e.key === 'ArrowRight' || e.key === 'ArrowUp' || e.key === 'ArrowDown') {
        setTimeout(handleSelection, 10);
      }
    };

    const handleClickOutside = (e: MouseEvent) => {
      // Hide tooltip when clicking outside
      const target = e.target as HTMLElement;
      if (!target.closest('[class*="tooltip"]')) {
        const selection = window.getSelection();
        if (selection && selection.toString().trim().length < MIN_SELECTION_LENGTH) {
          setTooltipVisible(false);
        }
      }
    };

    document.addEventListener('mouseup', handleMouseUp);
    document.addEventListener('keyup', handleKeyUp);
    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      document.removeEventListener('mouseup', handleMouseUp);
      document.removeEventListener('keyup', handleKeyUp);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isChatOpen]); // Add dependency so handler can check if chat is open

  const handleAskAboutSelection = (text: string) => {
    console.log('=== Ask About Selection Clicked ===');
    console.log('Text passed to handler:', text);
    console.log('Current selectedText state:', selectedText);
    console.log('==================================');

    // CRITICAL: Preserve the selected text before opening chat
    // This prevents it from being cleared when chat UI elements get selected
    setPreservedSelectedText(selectedText);
    console.log('Preserved selectedText:', selectedText);

    setInitialChatMode('selection');
    setIsChatOpen(true);
    setTooltipVisible(false);
  };

  const handleCloseChat = () => {
    console.log('=== Chat Closing ===');
    console.log('Clearing preserved text');

    setIsChatOpen(false);
    setPreservedSelectedText(''); // Clear preserved text
    setSelectedText(''); // Clear current selection
  };

  return (
    <>
      {children}
      <TextSelectionTooltip
        visible={tooltipVisible}
        position={tooltipPosition}
        selectedText={selectedText}
        onAskAbout={handleAskAboutSelection}
      />
      <AskTheTextbookButton onOpenChat={() => {
        setInitialChatMode('whole-book');
        setPreservedSelectedText(''); // Clear any preserved text for whole-book mode
        setIsChatOpen(true);
      }} />
      <ChatPanelPlaceholder
        isOpen={isChatOpen}
        onClose={handleCloseChat}
        selectedText={preservedSelectedText} // Use preserved text instead of current selection
        initialMode={initialChatMode}
      />
    </>
  );
}
