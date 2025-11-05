import React from 'react';

function ListItem({ title, description, createdDate, onIndex, isIndexing, isIndexed, onChat, isActiveChat }) {
  const formattedDate = createdDate ? new Date(createdDate).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }) : null;

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 mb-4 border transition-all duration-200 ${
      isActiveChat ? 'border-blue-500 shadow-lg ring-2 ring-blue-200' : 'border-gray-200 hover:shadow-lg'
    }`}>
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-xl font-semibold text-gray-800">
          {title}
        </h3>
        <div className="flex gap-2">
          <button
            onClick={onChat}
            disabled={!isIndexed}
            className={`
              flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200
              ${!isIndexed
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : isActiveChat
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-purple-50 text-purple-600 hover:bg-purple-100 hover:shadow-md active:scale-95'
              }
            `}
            title={!isIndexed ? 'Index document first to chat' : 'Chat with document'}
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </button>
          <button
            onClick={onIndex}
            disabled={isIndexing || isIndexed}
            className={`
              flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200
              ${isIndexed 
                ? 'bg-green-100 text-green-600 cursor-default' 
                : isIndexing 
                  ? 'bg-blue-100 text-blue-600 cursor-not-allowed' 
                  : 'bg-blue-50 text-blue-600 hover:bg-blue-100 hover:shadow-md active:scale-95'
              }
            `}
            title={isIndexed ? 'Indexed' : isIndexing ? 'Indexing...' : 'Index'}
          >
            {isIndexing ? (
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : isIndexed ? (
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            )}
          </button>
        </div>
      </div>
      
      {formattedDate && (
        <p className="text-sm text-gray-500 mb-2">
          Created: {formattedDate}
        </p>
      )}
      
      <p className="text-gray-600 leading-relaxed">
        {description}
      </p>
    </div>
  );
}

export default ListItem;

