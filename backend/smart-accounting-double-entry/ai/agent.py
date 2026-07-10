import json
import os
import google.generativeai as genai
from ai.prompts import PIANO_DEI_CONTI_SYSTEM_PROMPT

class AccountingAIAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.is_configured = api_key and api_key != "KEY"
        if self.is_configured:
            genai.configure(api_key=self.api_key)

    def interpret_line(self, line_description: str, candidate_accounts: list[dict]) -> dict:
        """
        Interprets a document line description and maps it to one of the candidate accounts.
        candidate_accounts: list of dicts with 'code', 'name', 'account_type'
        """
        if not self.is_configured:
            # Fallback mock logic for testing/trial
            desc_lower = line_description.lower()
            for acc in candidate_accounts:
                acc_name_lower = acc['name'].lower()
                # Direct match
                if acc_name_lower in desc_lower or desc_lower in acc_name_lower:
                    return {
                        "proposed_account": acc['name'],
                        "confidence_score": 0.95,
                        "reason": f"Found direct match in candidate account name for '{line_description}'"
                    }
                # Word-by-word heuristic matching
                words = [w for w in acc_name_lower.split() if len(w) >= 4]
                if any(w in desc_lower for w in words):
                    return {
                        "proposed_account": acc['name'],
                        "confidence_score": 0.92,
                        "reason": f"Found word overlap match in candidate account name for '{line_description}'"
                    }
            # Default fallback matching
            proposed = candidate_accounts[0]['name'] if candidate_accounts else "Spese di Manutenzione Immobili"
            return {
                "proposed_account": proposed,
                "confidence_score": 0.90,
                "reason": "Default fallback mapping in mock mode"
            }

        try:
            # Configure structured output with Gemini 2.0
            model = genai.GenerativeModel(
                "gemini-2.0-flash",
                system_instruction=PIANO_DEI_CONTI_SYSTEM_PROMPT,
                generation_config={"response_mime_type": "application/json"}
            )
            
            accounts_formatted = json.dumps(candidate_accounts, indent=2)
            prompt = f"""
            Document line description: "{line_description}"
            
            Available accounts in the Piano dei Conti:
            {accounts_formatted}
            
            Choose the most appropriate account from the list above. Return your output strictly as a JSON object with:
            {{
              "proposed_account": "Account Name",
              "confidence_score": 0.0 to 1.0,
              "reason": "Short explanation of your choice"
            }}
            """
            response = model.generate_content(prompt)
            result = json.loads(response.text.strip())
            return result
        except Exception as e:
            # Fallback on API failure
            desc_lower = line_description.lower()
            for acc in candidate_accounts:
                if acc['name'].lower() in desc_lower or desc_lower in acc['name'].lower():
                    return {
                        "proposed_account": acc['name'],
                        "confidence_score": 0.85,
                        "reason": f"Fallback match on API failure for '{line_description}'"
                    }
            proposed = candidate_accounts[0]['name'] if candidate_accounts else "Spese di Manutenzione Immobili"
            return {
                "proposed_account": proposed,
                "confidence_score": 0.50,
                "reason": f"Fallback due to Gemini API failure: {str(e)}"
            }
