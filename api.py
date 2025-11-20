from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import tempfile
import os
from contextlib import asynccontextmanager
from playwright_to_schema_migrator import PlaywrightToSchemaMigrator

class CodeInput(BaseModel):
    code: str

class MigratorWithOpenAI(PlaywrightToSchemaMigrator):
    def __init__(self, openai_api_key: str):
        import openai
        self.client = openai.OpenAI(api_key=openai_api_key)
    
    def extract_playwright_actions(self, script_content: str):
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
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            
            content = response.choices[0].message.content
            json_start = content.find('[')
            json_end = content.rfind(']') + 1
            if json_start != -1 and json_end != -1:
                import json
                return json.loads(content[json_start:json_end])
        except:
            pass
        
        return []

# Move app initialization after lifespan definition

# Initialize migrator (API key will be set via environment variable)
migrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global migrator
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is required")
    migrator = MigratorWithOpenAI(api_key)
    yield

app = FastAPI(title="Playwright to Schema Migrator API", lifespan=lifespan)

@app.post("/migrate/text")
async def migrate_from_text(input_data: CodeInput):
    """Migrate Playwright code from text input"""
    try:
        actions = migrator.extract_playwright_actions(input_data.code)
        
        if not actions:
            actions = migrator._manual_parse(input_data.code)
        
        schema_steps = []
        for i, action in enumerate(actions, 1):
            schema_command = migrator.map_to_schema_command(action)
            if schema_command:
                schema_command['order'] = i
                schema_steps.append(schema_command)
        
        schema = [{
            "steps": schema_steps,
            "name": "migratedTest",
            "description": "Migrated from Playwright test",
            "base_url": migrator._extract_base_url(input_data.code)
        }]
        
        return {"schema": schema}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/migrate/file")
async def migrate_from_file(file: UploadFile = File(...)):
    """Migrate Playwright code from uploaded file"""
    try:
        content = await file.read()
        script_content = content.decode('utf-8')
        
        actions = migrator.extract_playwright_actions(script_content)
        
        if not actions:
            actions = migrator._manual_parse(script_content)
        
        schema_steps = []
        for i, action in enumerate(actions, 1):
            schema_command = migrator.map_to_schema_command(action)
            if schema_command:
                schema_command['order'] = i
                schema_steps.append(schema_command)
        
        schema = [{
            "steps": schema_steps,
            "name": "migratedTest",
            "description": "Migrated from Playwright test",
            "base_url": migrator._extract_base_url(script_content)
        }]
        
        return {"schema": schema}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)