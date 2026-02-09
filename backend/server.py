from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import pandas as pd
import io
from dotenv import load_dotenv
import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import re
import boto3
from botocore.exceptions import ClientError
from context import generate_prompt
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



# Load environment variables
load_dotenv(override=True)

# Load configuration from environment variables
USE_S3 = os.getenv("USE_S3", "false").lower() == "true"
S3_BUCKET = os.getenv("S3_BUCKET", "")
MEMORY_DIR = os.getenv("MEMORY_DIR", "../memory")
USE_BEDROCK = os.getenv("USE_BEDROCK", "false").lower() == "true"
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")



app = FastAPI()

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if USE_BEDROCK:
    # Initialize Bedrock client
    bedrock_client = boto3.client(
        service_name="bedrock-runtime", 
        region_name=os.getenv("DEFAULT_AWS_REGION", "us-east-1")
    )
    llm_version = BEDROCK_MODEL_ID
else:
    # Initialize OpenAI client if not using Bedrock
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    llm_version = "gpt-4o-mini" 


# Initialize S3 client if needed
if USE_S3:
    s3_client = boto3.client("s3")


def save_files(
    transactions: pd.DataFrame, 
    original_filename: str,
    analysis_result: List[Dict]):

    """
    Save the uploaded transactions DataFrame, analysis results (JSON), and metadata.
    Uses S3 if USE_S3 is True; otherwise saves locally.
    """
    # Create a unique folder name per uploaded file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{Path(original_filename).stem}_{timestamp}"


    if USE_S3:
        # Save original CSV to S3
        csv_buffer = io.StringIO()
        transactions.to_csv(csv_buffer, index=False)
        csv_key = f"{folder_name}/{original_filename}"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=csv_key,
            Body=csv_buffer.getvalue(),
            ContentType="text/csv"
        )

        # Save analysis JSON to S3
        json_key = f"{folder_name}/analysis.json"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=json_key,
            Body=json.dumps(analysis_result, indent=2, ensure_ascii=False),
            ContentType="application/json"
        )
       
        # Save metadata JSON to S3
        metadata = {
            "original_filename": original_filename,
            "uploaded_at": timestamp,
            "num_transactions": len(transactions),
            "num_suspicious": len(analysis_result),
            "llm_version": llm_version 
        }
        metadata_key = f"{folder_name}/metadata.json"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=metadata_key,
            Body=json.dumps(metadata, indent=2, ensure_ascii=False),
            ContentType="application/json"
        )
       
    else:
        # Local storage
        memory_dir = Path(MEMORY_DIR)
        folder_path = memory_dir / folder_name
        folder_path.mkdir(exist_ok=True, parents=True)

        #Save original CSV locally
        csv_path = folder_path / original_filename
        transactions.to_csv(csv_path, index=False)
       
        # Save analysis JSON locally
        json_path = folder_path / "analysis.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)

        # Save metadata JSON locally
        metadata = {
            "original_filename": original_filename,
            "uploaded_at": timestamp,
            "num_transactions": len(transactions),
            "num_suspicious": len(analysis_result),
            "llm_version": llm_version
        }
        metadata_path = folder_path / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
       

 

def call_bedrock(system_prompt: str, user_prompt: str) -> str:
    
    try:
        prompt_text = system_prompt + "\n" + user_prompt

        payload = {
            "inputText": prompt_text,
            "inferenceConfig": {
                "maxTokens": 2000,
                "temperature": 0.7,
                "topP": 0.9
            }
        }
        
        response = bedrock_client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )
        return response["output"]["message"]["content"][0]["text"]

    except Exception as e:
        logger.exception("Bedrock error")
        raise HTTPException(status_code=500, detail=f"Bedrock error: {str(e)}")

    
def call_openai(system_prompt: str, user_prompt: str) -> str:

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
        ]
        
    response = client.chat.completions.create(
        model="gpt-4o-mini",
         messages=messages
        )

    #Exctract text output from the model
    return response.choices[0].message.content

 


def extract_json(text: str) -> str:
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ```
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    return text


@app.get("/")
async def root():
    return {"message": "AI Transaction Guardian Service",
            "memory_enabled": USE_S3,
            "storage": "S3" if USE_S3 else "local",
            "bedrock_enabled": USE_BEDROCK,
            "llm_model":llm_version
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "use_s3": USE_S3,
        "use_bedrock": USE_BEDROCK,
    }


@app.post("/analyze")
async def analyze_transactions(file: UploadFile = File(...)):
    
    try:
        contents = await file.read()
        transactions = pd.read_csv(io.StringIO(contents.decode("utf-8")))

        system_prompt, user_prompt = generate_prompt(transactions)

        if USE_BEDROCK:
            llm_output = call_bedrock(system_prompt, user_prompt)
        else:
            llm_output = call_openai(system_prompt, user_prompt)
            

        clean_output = extract_json(llm_output)

        try:
            fraud_data = json.loads(clean_output)
  

        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse JSON from model: {e}\nRaw output: {llm_output}"
            )
    
        save_files(transactions, file.filename, fraud_data)


        return {"fraud_analysis": fraud_data}

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Uploaded CSV is empty")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="CSV parse error")
    except Exception as e:
        import traceback
        logger.exception("Unhandled error during analysis")
        raise HTTPException(status_code=500, detail="Internal server error")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
