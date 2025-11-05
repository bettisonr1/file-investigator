import React, { useState, useEffect } from 'react';
import ListItem from './ListItem';
import DragDropArea from './DragDropArea';
import ChatWindow from './ChatWindow';
import { indexFile, updateFileIndexStatus } from '../services/uploadService';

function ListContainer() {
  const [items, setItems] = useState([]);
  const [activeChatItem, setActiveChatItem] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Helper function to map file data from MongoDB to item format
  const mapFileToItem = (file) => ({
    id: file._id?.$oid || Date.now() + Math.random(),
    title: file.file_name || 'Unknown File',
    description: `File: ${file.file_name || 'Unknown'}`,
    createdDate: Date.now(),
    isIndexed: file.indexed === true, // File is indexed based on the 'indexed' field from backend
    isIndexing: false,
    datastoreId: file.datastore_id || null,
    datastoreName: file.datastore_id || null,
    datastoreDisplayName: file.datastore_id || null
  });

  // Helper function to fetch files from backend
  const fetchFiles = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/files');
      const result = await response.json();
      
      if (result.success) {
        const filesData = JSON.parse(result.data);
        const mappedItems = filesData.map(mapFileToItem);
        setItems(mappedItems);
        return true;
      } else {
        console.error('Failed to fetch files:', result.error);
        return false;
      }
    } catch (error) {
      console.error('Error fetching files:', error);
      return false;
    }
  };

  // Fetch files from backend on component mount
  useEffect(() => {
    const loadFiles = async () => {
      await fetchFiles();
      setIsLoading(false);
    };

    loadFiles();
  }, []);

  const handleFileUploaded = async (fileData) => {
    // Refresh the file list from the backend to get the most up-to-date data
    const success = await fetchFiles();
    
    if (!success) {
      // Fallback: add the item locally if refresh fails
      const newItem = {
        id: Date.now(),
        title: fileData.fileName || 'Uploaded File',
        description: fileData.description || `File uploaded: ${fileData.fileName || 'Unknown file'}`,
        createdDate: Date.now(),
        isIndexed: false,
        isIndexing: false,
        datastoreDisplayName: fileData.datastore?.displayName || null,
        datastoreId: fileData.datastore?.datastoreId || null,
        datastoreName: fileData.datastore?.datastoreName || null
      };
      setItems([...items, newItem]);
    }
  };

  const handleIndex = async (item) => {
    // Check if datastore information is available
    if (!item.datastoreDisplayName) {
      console.error('Cannot index: No datastore information available for this item');
      alert('Cannot index: This file does not have an associated datastore. Please re-upload the file.');
      return;
    }

    // Set the item to indexing state
    setItems(items.map(i => 
      i.id === item.id 
        ? { ...i, isIndexing: true }
        : i
    ));

    try {
      // Step 1: Index the file in Vertex AI
      const result = await indexFile(item.title, item.datastoreId);
      
      if (result.success) {
        // Step 2: Mark the file as indexed in MongoDB
        const updateResult = await updateFileIndexStatus(item.id, true);
        
        if (updateResult.success) {
          console.log('✅ File marked as indexed in database');
          // Step 3: Refresh files from backend to get updated status
          await fetchFiles();
        } else {
          console.error('⚠️ File indexed but failed to update database:', updateResult.error);
          // Still refresh to get current state
          await fetchFiles();
        }
      } else {
        // Reset to not indexing on error
        console.error('Indexing failed:', result.error);
        alert(`Indexing failed: ${result.error}`);
        setItems(items.map(i => 
          i.id === item.id 
            ? { ...i, isIndexing: false }
            : i
        ));
      }
    } catch (error) {
      console.error('Indexing error:', error);
      alert(`Indexing error: ${error.message}`);
      // Reset to not indexing on error
      setItems(items.map(i => 
        i.id === item.id 
          ? { ...i, isIndexing: false }
          : i
      ));
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const handleChatOpen = (item) => {
    if (item.isIndexed) {
      setActiveChatItem(item);
    }
  };

  const handleChatClose = () => {
    setActiveChatItem(null);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left side - List and Upload Area */}
      <div className={`flex-1 overflow-y-auto p-6 transition-all duration-300 ${activeChatItem ? 'mr-2' : ''}`}>
        <div className="max-w-3xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Item List</h1>
            <p className="text-gray-600">Manage your list items below</p>
          </div>
          
          <div className="mb-6">
            {isLoading ? (
              <div className="text-center py-8">
                <p className="text-gray-500">Loading files...</p>
              </div>
            ) : items.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-500">No files yet. Upload a file to get started.</p>
              </div>
            ) : (
              items.map((item) => (
                <ListItem
                  key={item.id}
                  title={item.title}
                  description={item.description}
                  createdDate={item.createdDate}
                  onIndex={() => handleIndex(item)}
                  isIndexing={item.isIndexing}
                  isIndexed={item.isIndexed}
                  onChat={() => handleChatOpen(item)}
                  isActiveChat={activeChatItem?.id === item.id}
                />
              ))
            )}
          </div>

          <div className="mt-8">
            <DragDropArea onFileUploaded={handleFileUploaded} />
          </div>
        </div>
      </div>

      {/* Right side - Chat Window */}
      {activeChatItem && (
        <div className="w-[500px] flex-shrink-0 p-6 pl-2">
          <div className="h-full">
            <ChatWindow
              documentTitle={activeChatItem.title}
              documentId={activeChatItem.id}
              datastoreLocation={activeChatItem.datastoreId}
              onClose={handleChatClose}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default ListContainer;

