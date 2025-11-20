#!/usr/bin/env python3

import json
import os
import re
import requests
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class PlaywrightToSchemaMigrator:
    def __init__(self, ollama_url: str = ""):
        self.ollama_url = ollama_url or os.getenv('OLLAMA_URL', 'http://localhost:11434')
        
    def extract_playwright_actions(self, script_content: str) -> List[Dict[str, Any]]:
        """Extract actions from Playwright script using OLLAMA"""
        
        prompt = f"""
        Analyze this Playwright test script and extract all the actions in a structured format.
        
        Script:
        {script_content}
        
        Extract each action with:
        1. Action type (goto, fill, click, select_option, upload, hover, etc.)
        2. Selector (CSS selector, ID, etc.)
        3. Value (if applicable)
        4. Description
        
        Return as JSON array with format:
        [
            {{
                "action": "goto",
                "selector": "",
                "value": "https://example.com/onboarding/complex",
                "description": "Navigate to onboarding page"
            }},
            {{
                "action": "fill",
                "selector": "#firstName",
                "value": "Gul",
                "description": "Fill first name field"
            }}
        ]
        """
        
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            try:
                # Extract JSON from response
                content = result['response']
                json_start = content.find('[')
                json_end = content.rfind(']') + 1
                if json_start != -1 and json_end != -1:
                    return json.loads(content[json_start:json_end])
            except:
                pass
        
        return []
    
    def map_to_schema_command(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Map Playwright action to schema command using OLLAMA"""
        
        # Load sample schema for reference
        sample_schema_path = os.getenv('SAMPLE_SCHEMA_PATH', '/Users/aarij.hussaan/development/schema_migrator/sample_schemas/CustomerCreate.json')
        with open(sample_schema_path, 'r') as f:
            sample_schema = json.load(f)
        
        prompt = f"""
        Map this Playwright action to the schema format based on the sample schema structure.
        
        Playwright Action:
        {json.dumps(action, indent=2)}
        
        Sample Schema Commands (for reference):
        - visit: Navigate to URL
        - type: Fill text input
        - click: Click element
        - select: Select dropdown option
        - keypress: Press keyboard key
        - upload: Upload file
        
        Generate a schema command in this exact format:
        {{
            "command": {{
                "name": "type|click|visit|select|keypress",
                "fields": [
                    {{
                        "name": "field_name",
                        "type": "text",
                        "label": "Label",
                        "value": "actual_value",
                        "required": true
                    }}
                ]
            }},
            "order": 1
        }}
        
        Map the action type correctly:
        - goto -> visit
        - fill -> type
        - click -> click
        - select_option -> select
        - upload -> upload (not in sample but infer structure)
        """
        
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            try:
                content = result['response']
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    return json.loads(content[json_start:json_end])
            except:
                pass
        
        # Fallback mapping
        return self._fallback_mapping(action)
    
    def _fallback_mapping(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback mapping when OLLAMA fails"""
        action_type = action.get('action', '')
        
        if action_type == 'goto':
            return {
                "command": {
                    "name": "visit",
                    "fields": [
                        {
                            "name": "visit",
                            "type": "text",
                            "label": "Browse to URL",
                            "value": action.get('value', ''),
                            "required": True
                        }
                    ]
                }
            }
        elif action_type == 'fill':
            return {
                "command": {
                    "name": "type",
                    "fields": [
                        {
                            "name": "name",
                            "type": "text",
                            "label": "Name",
                            "value": action.get('value', ''),
                            "required": True
                        },
                        {
                            "name": "css_path",
                            "type": "text",
                            "label": "CSS Path",
                            "value": action.get('selector', ''),
                            "required": True
                        }
                    ]
                }
            }
        elif action_type == 'click':
            return {
                "command": {
                    "name": "click",
                    "fields": [
                        {
                            "name": "name",
                            "type": "text",
                            "label": "Name",
                            "value": action.get('description', 'Click element'),
                            "required": True
                        },
                        {
                            "name": "css_path",
                            "type": "text",
                            "label": "CSS Path",
                            "value": action.get('selector', ''),
                            "required": True
                        }
                    ]
                }
            }
        elif action_type == 'select_option':
            return {
                "command": {
                    "name": "select",
                    "fields": [
                        {
                            "name": "name",
                            "type": "text",
                            "label": "Name",
                            "value": action.get('description', 'Select option'),
                            "required": True
                        },
                        {
                            "name": "css_path",
                            "type": "text",
                            "label": "CSS Path",
                            "value": action.get('selector', ''),
                            "required": True
                        },
                        {
                            "name": "value",
                            "type": "text",
                            "label": "Option Value",
                            "value": action.get('value', ''),
                            "required": True
                        }
                    ]
                }
            }
        elif action_type == 'upload':
            return {
                "command": {
                    "name": "upload",
                    "fields": [
                        {
                            "name": "name",
                            "type": "text",
                            "label": "Name",
                            "value": action.get('description', 'Upload file'),
                            "required": True
                        },
                        {
                            "name": "css_path",
                            "type": "text",
                            "label": "CSS Path",
                            "value": action.get('selector', ''),
                            "required": True
                        },
                        {
                            "name": "file_path",
                            "type": "text",
                            "label": "File Path",
                            "value": action.get('value', ''),
                            "required": True
                        }
                    ]
                }
            }
        elif action_type == 'hover':
            return {
                "command": {
                    "name": "hover",
                    "fields": [
                        {
                            "name": "name",
                            "type": "text",
                            "label": "Name",
                            "value": action.get('description', 'Hover element'),
                            "required": True
                        },
                        {
                            "name": "css_path",
                            "type": "text",
                            "label": "CSS Path",
                            "value": action.get('selector', ''),
                            "required": True
                        }
                    ]
                }
            }
        
        return {}
    
    def migrate_script(self, script_path: str, output_path: str):
        """Migrate Playwright script to schema format"""
        
        # Read the script
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        print("Extracting actions from Playwright script...")
        actions = self.extract_playwright_actions(script_content)
        
        if not actions:
            print("Failed to extract actions, using manual parsing...")
            actions = self._manual_parse(script_content)
        
        print(f"Extracted {len(actions)} actions")
        
        # Convert to schema format
        schema_steps = []
        for i, action in enumerate(actions, 1):
            print(f"Converting action {i}: {action.get('action', 'unknown')}")
            schema_command = self.map_to_schema_command(action)
            if schema_command:
                schema_command['order'] = i
                schema_steps.append(schema_command)
        
        # Create final schema
        schema = [{
            "steps": schema_steps,
            "name": "migratedTest",
            "description": "Migrated from Playwright test",
            "base_url": self._extract_base_url(script_content)
        }]
        
        # Save to file
        with open(output_path, 'w') as f:
            json.dump(schema, f, indent=2)
        
        print(f"Migration complete! Schema saved to {output_path}")
        return schema
    
    def _manual_parse(self, script_content: str) -> List[Dict[str, Any]]:
        """Manual parsing as fallback"""
        actions = []
        
        # Extract goto
        goto_match = re.search(r'page\.goto\("([^"]+)"\)', script_content)
        if goto_match:
            actions.append({
                "action": "goto",
                "selector": "",
                "value": goto_match.group(1),
                "description": "Navigate to page"
            })
        
        # Extract text fields sections
        text_sections = re.findall(r'text_fields_\w+\s*=\s*{([^}]+)}', script_content, re.DOTALL)
        for section in text_sections:
            pairs = re.findall(r'"([^"]+)":\s*"([^"]+)"', section)
            for selector, value in pairs:
                actions.append({
                    "action": "fill",
                    "selector": selector,
                    "value": value,
                    "description": f"Fill {selector}"
                })
        
        # Extract dropdown sections
        dropdown_sections = re.findall(r'dropdowns_\w+\s*=\s*{([^}]+)}', script_content, re.DOTALL)
        for section in dropdown_sections:
            pairs = re.findall(r'"([^"]+)":\s*"([^"]+)"', section)
            for selector, option in pairs:
                actions.append({
                    "action": "select_option",
                    "selector": selector,
                    "value": option,
                    "description": f"Select {option} in {selector}"
                })
        
        # Extract file upload sections
        upload_sections = re.findall(r'file_uploads\s*=\s*{([^}]+)}', script_content, re.DOTALL)
        for section in upload_sections:
            pairs = re.findall(r'"([^"]+)":\s*"([^"]+)"', section)
            for selector, file_path in pairs:
                actions.append({
                    "action": "upload",
                    "selector": selector,
                    "value": file_path,
                    "description": f"Upload file to {selector}"
                })
        
        # Extract direct page.fill calls (for loops)
        fill_matches = re.findall(r'page\.fill\(f"([^"]+)",\s*f"([^"]+)"\)', script_content)
        for selector, value in fill_matches:
            actions.append({
                "action": "fill",
                "selector": selector,
                "value": value,
                "description": f"Fill {selector}"
            })
        
        # Extract direct page.select_option calls (for loops)
        select_matches = re.findall(r'page\.select_option\(f"([^"]+)",\s*"([^"]+)"\)', script_content)
        for selector, option in select_matches:
            actions.append({
                "action": "select_option",
                "selector": selector,
                "value": option,
                "description": f"Select {option} in {selector}"
            })
        
        # Extract click actions
        click_matches = re.findall(r'page\.click\("([^"]+)"\)', script_content)
        for selector in click_matches:
            actions.append({
                "action": "click",
                "selector": selector,
                "value": "",
                "description": f"Click {selector}"
            })
        
        # Extract hover actions
        hover_matches = re.findall(r'page\.hover\("([^"]+)"\)', script_content)
        for selector in hover_matches:
            actions.append({
                "action": "hover",
                "selector": selector,
                "value": "",
                "description": f"Hover {selector}"
            })
        
        return actions
    
    def _extract_base_url(self, script_content: str) -> str:
        """Extract base URL from script"""
        goto_match = re.search(r'page\.goto\("([^"]+)"\)', script_content)
        if goto_match:
            url = goto_match.group(1)
            # Extract base URL
            if '://' in url:
                parts = url.split('/')
                return f"{parts[0]}//{parts[2]}"
        return ""

def main():
    migrator = PlaywrightToSchemaMigrator()
    
    script_path = os.getenv('SCRIPT_PATH', '/Users/aarij.hussaan/development/schema_migrator/sample_scripts/test_2.py')
    output_path = os.getenv('OUTPUT_PATH', '/Users/aarij.hussaan/development/schema_migrator/migrated_schema.json')
    
    try:
        schema = migrator.migrate_script(script_path, output_path)
        print("\nMigration Summary:")
        print(f"- Generated {len(schema[0]['steps'])} steps")
        print(f"- Output saved to: {output_path}")
        
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    main()