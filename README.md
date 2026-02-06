# AI Transaction Guardian
AI Transaction Guardian is a FastAPI service for analyzing transaction data using large language models (OpenAI GPT or Amazon Bedrock). It supports CSV uploads, detects suspicious transactions, and stores results locally or in S3.

### 🚀 Features 
---
- Upload CSV files via API
- Analyze transactions with AI LLMs
- Supports multiple AI backends:
  1. 🧠 OpenAI GPT models
  2. ☁️ AWS Bedrock models
- 🗄️ Save results:
  1. 💻 Local storage
  2. ☁️ AWS S3 storage
- 📊 Returns analysis in JSON format





Tech Stack

Backend: Python, FastAPI

AI: OpenAI GPT / Amazon Bedrock

Data processing: Pandas

Storage: Local files or AWS S3

Deployment: AWS Lambda compatible
