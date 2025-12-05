import React, { useState } from 'react';
import AskTheTextbookButton from '@site/src/components/chat/AskTheTextbookButton';
import ChatPanelPlaceholder from '@site/src/components/chat/ChatPanelPlaceholder';

export default function Root({ children }: { children: React.ReactNode }): JSX.Element {
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <>
      {children}
      <AskTheTextbookButton onOpenChat={() => setIsChatOpen(true)} />
      <ChatPanelPlaceholder
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
      />
    </>
  );
}
