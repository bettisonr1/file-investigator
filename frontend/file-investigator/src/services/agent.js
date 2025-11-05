import { LlmAgent } from "@google/adk"
import { vertex_ai_search_tool } from "./vertexSearchTool"

doc_search_agent = LlmAgent(
    {
        name: "doc_search_agent",
        model: "gemini-2-flash",
        tools: [vertex_ai_search_tool],
        instruction: `You are a helpful document investigator assistant that answers questions based on information found in the document store consisting of a single document.
        Use the 'vertex_ai_search_tool' to find out relevant information from the document before answering.
        If the answer isn't in the document, say that you couldn't find the information.
        If the question is not related to the document, say that you don't know the answer.
        `,
        description: "Answers questions using a specific Vertex AI Search datastore.",
    }
)