import { Outlet } from 'react-router-dom';
import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import TopBar from '../components/TopBar';
import ComposePopup from '../components/ComposePopup';

export default function AppLayout() {
  const [showCompose, setShowCompose] = useState(false);
  const [editingDraft, setEditingDraft] = useState(null);

  const handleCompose = () => {
    setEditingDraft(null);
    setShowCompose(true);
  };

  const handleCloseCompose = () => {
    setShowCompose(false);
    setEditingDraft(null);
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-100 border-r h-full">
        <Sidebar onCompose={handleCompose} />
      </aside>

      {/* Main Panel */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <TopBar />
        <div className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </div>
      </div>

      {/* Compose Popup */}
      {showCompose && (
        <ComposePopup
          draft={editingDraft}
          onClose={handleCloseCompose}
        />
      )}
    </div>
  );
}
