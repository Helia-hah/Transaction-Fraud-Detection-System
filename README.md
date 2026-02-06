# AI Transaction Guardian
AI Transaction Guardian is a FastAPI service for analyzing transaction data using large language models (OpenAI GPT or Amazon Bedrock). It supports CSV uploads, detects suspicious transactions, and stores results locally or in S3.

### 🚀 Features 
---
- Upload CSV files via API
- Analyze transactions with AI LLMs
- Supports multiple AI backends:
  1. 🧠 OpenAI GPT models
  2. ☁️ AWS Bedrock models
- Save results:
  1. 💻 Local storage
  2. ☁️ AWS S3 storage
- Returns analysis in JSON format

### 🛠️ Tech Stack
---
- **Backend**: Python, FastAPI
- **Frontend**: Next.js, Tailwind CSS
- **AI / LLM**: OpenAI GPT, Amazon Bedrock
- **Storage**: Local files, AWS S3
- **Deployment**: AWS Lambda
- **API Gateway**: AWS API Gateway
- **CDN / Delivery**: AWS CloudFront
