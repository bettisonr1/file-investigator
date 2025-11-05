import { FunctionTool } from '@google/adk';
import { z } from 'zod';
import { searchVertexAI } from './vertexSearchService';

/**
 * Creates a Vertex AI Search tool for use with LlmAgent
 * @returns {FunctionTool} Configured tool instance
 */
export const vertex_ai_search_tool = new FunctionTool({
    name: 'vertex_ai_search',
    description: 'Search through the document store using Vertex AI Search. Use this to find relevant information from uploaded documents when answering questions.',
    parameters: z.object({
      query: z.string().describe('The search query to find relevant documents')
    }),
    execute: async ({ query }) => {
      console.log('Searching with query:', query);
      const result = await searchVertexAI(query);
      
      if (result.success) {
        // Return the search results in a format the agent can understand
        return {
          results: result.data.results || [],
          summary: result.data.summary || 'No summary available'
        };
      } else {
        throw new Error(result.error || 'Search failed');
      }
    }
  });

