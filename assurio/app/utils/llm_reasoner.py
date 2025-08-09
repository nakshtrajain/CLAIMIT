import json
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from config import settings

class LLMReasoner:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-1.5-flash",  # ✅ or "models/gemini-1.5-pro"
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.2
        )
        
        self.prompt_template = PromptTemplate(
            input_variables=["query", "retrieved_chunks"],
            template="""
You are a claims analyst assistant. A user has asked a question related to an insurance policy.
You are provided:
- A query from the user.
- Retrieved clauses from the policy document.

You must:
1. Understand the context from the user's query.
2. Analyze relevant clauses.
3. Return a structured JSON in the format:

{{
  "decision": "approved/rejected",
  "amount": "if applicable",
  "justification": "why this decision was made",
  "referenced_clauses": [exact text]
}}

---

User Query: {query}

Retrieved Clauses:
{retrieved_chunks}

Please analyze the query and retrieved clauses to provide a decision. Be specific about which clauses support your decision.
"""
        )
    
    async def reason(self, query: str, retrieved_documents: List[Document]) -> Dict[str, Any]:
        """Reason over retrieved documents and return decision"""
        try:
            # Format retrieved chunks
            chunks_text = "\n\n".join([
                f"Clause {i+1}: {doc.page_content}"
                for i, doc in enumerate(retrieved_documents)
            ])
            
            # Create prompt
            prompt = self.prompt_template.format(
                query=query,
                retrieved_chunks=chunks_text
            )
            
            # Get LLM response
            response = await self.llm.ainvoke(prompt)
            response_text = response.content.strip()
            
            # Try to parse JSON from response
            try:
                # Extract JSON from response (in case there's extra text)
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = response_text[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    # Fallback: try to parse the entire response
                    result = json.loads(response_text)
                    
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response
                result = {
                    "decision": "error",
                    "amount": "N/A",
                    "justification": f"Failed to parse LLM response: {response_text}",
                    "referenced_clauses": []
                }
            
            # Ensure all required fields are present
            required_fields = ["decision", "amount", "justification", "referenced_clauses"]
            for field in required_fields:
                if field not in result:
                    result[field] = "N/A" if field != "referenced_clauses" else []
            
            return result
            
        except Exception as e:
            return {
                "decision": "error",
                "amount": "N/A",
                "justification": f"Error in reasoning: {str(e)}",
                "referenced_clauses": []
            }
    
    async def extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from user query using LLM"""
        try:
            entity_prompt = f"""
Extract key entities from the following insurance query. Return as JSON:

Query: {query}

Return JSON with these fields:
{{
  "age": "extracted age or age range",
  "procedure": "medical procedure or treatment",
  "location": "geographic location",
  "policy_type": "type of insurance policy",
  "duration": "policy duration if mentioned"
}}

If any field is not found, use "N/A".
"""
            
            response = await self.llm.ainvoke(entity_prompt)
            response_text = response.content.strip()
            
            # Try to parse JSON
            try:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = response_text[start_idx:end_idx]
                    entities = json.loads(json_str)
                else:
                    entities = json.loads(response_text)
                    
            except json.JSONDecodeError:
                entities = {
                    "age": "N/A",
                    "procedure": "N/A", 
                    "location": "N/A",
                    "policy_type": "N/A",
                    "duration": "N/A"
                }
            
            return entities
            
        except Exception as e:
            return {
                "age": "N/A",
                "procedure": "N/A",
                "location": "N/A", 
                "policy_type": "N/A",
                "duration": "N/A",
                "error": str(e)
            } 