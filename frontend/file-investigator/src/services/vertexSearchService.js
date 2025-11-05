const API_BASE_URL = process.env.BACKEND_URL || 'http://localhost:8080';

/**
 * Search the Vertex AI Search datastore
 * @param {string} query - The search query
 * @returns {Promise<Object>} - Response with search results
 */
export const searchVertexAI = async (query) => {
  try {
    // This will call your backend endpoint for Vertex AI Search
    const response = await fetch(`${API_BASE_URL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        message: 'Search failed',
      }));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return {
      success: true,
      data: data,
    };
  } catch (error) {
    console.error('Vertex AI Search error:', error);
    return {
      success: false,
      error: error.message || 'Failed to search',
    };
  }
};

