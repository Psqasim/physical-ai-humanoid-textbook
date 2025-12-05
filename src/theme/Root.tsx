import React, { useState, useEffect } from 'react';
import AskTheTextbookButton from '@site/src/components/chat/AskTheTextbookButton';
import ChatPanelPlaceholder from '@site/src/components/chat/ChatPanelPlaceholder';
import TextSelectionTooltip from '@site/src/components/chat/TextSelectionTooltip';

const MIN_SELECTION_LENGTH = 10;

export default function Root({ children }: { children: React.ReactNode }): JSX.Element {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [tooltipVisible, setTooltipVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });
  const [initialChatMode, setInitialChatMode] = useState<'whole-book' | 'selection'>('whole-book');

  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      if (!selection) return;

      const text = selection.toString().trim();

      if (text.length >= MIN_SELECTION_LENGTH) {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        // Position tooltip above and centered on the selection
        const top = rect.top + window.scrollY - 50; // 50px above selection
        const left = rect.left + window.scrollX + rect.width / 2 - 75; // Center tooltip (assuming ~150px width)

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
  }, []);

  const handleAskAboutSelection = (text: string) => {
    setInitialChatMode('selection');
    setIsChatOpen(true);
    setTooltipVisible(false);
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
        setIsChatOpen(true);
      }} />
      <ChatPanelPlaceholder
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
        selectedText={selectedText}
        initialMode={initialChatMode}
      />
    </>
  );
}
