# SIH AI Service

Python-based AI service for the **Smart India Hackathon 2026** project.

This service is responsible for understanding and analyzing societal challenges submitted to the main SIH platform through text, images, and audio.

The service processes the submitted information and returns structured JSON that can be consumed by the backend service.

---

## SIH Problem

**Problem Statement:** SIH26043

**Title:** A digital platform to crowdsource societal challenges and facilitate collaborative problem solving through universities and industry partnerships.

The overall platform allows societal challenges to be submitted and processed so that they can be categorized, prioritized, matched with similar challenges, and routed for further problem solving.

This repository contains **only the AI service component**.

---

# Scope of This Service

## V1 — Current Version

The AI service supports:

- Text-based challenge analysis
- Image analysis
- Audio transcription
- Multimodal challenge understanding
- Semantic categorization
- Problem information extraction
- Priority scoring
- Similarity and duplicate detection
- AI-generated explanation
- Structured JSON output

## V2 — Future

Video processing will be added in a future version.

**Video processing is intentionally out of scope for V1.**

---

# AI Pipeline

The current processing flow is:

```text
                 User Submission
                       |
          +------------+------------+
          |            |            |
        Text         Image        Audio
          |            |            |
          |           CLIP        Whisper
          |            |            |
          +------------+------------+
                       |
                 Multimodal Fusion
                       |
                       v
              Challenge Understanding
                       |
        +--------------+--------------+
        |              |              |
   Categorization  Extraction      Priority
        |              |              |
        +--------------+--------------+
                       |
                Similarity Check
                       |
                  Explanation
                       |
                       v
                 Structured JSON
                       |
                       v
                Backend Service
```

---

# Supported Input Types

## Text

The primary challenge description is provided as text.

Example:

```text
Farmers in rural villages are facing crop losses
due to poor irrigation facilities.
```

The service extracts information such as:

- Problem
- Affected group
- Location
- Causes
- Impact

---

## Image

Images can be submitted along with a challenge.

The service uses image analysis to determine the relevant societal domain.

Processing flow:

```text
Image
  |
  v
CLIP
  |
  v
Domain Classification
```

The service also validates the image and extracts basic image information such as dimensions and format.

---

## Audio

Audio submissions are transcribed locally using Whisper.

Processing flow:

```text
Audio
  |
  v
Whisper
  |
  v
Text Transcription
  |
  v
AI Analysis
```

Audio is converted into text before being incorporated into the challenge analysis pipeline.

---

# Supported Domains

The V1 semantic classifier currently recognizes the following domains:

| Domain ID | Domain |
|---|---|
| `disaster_management` | Disaster Management |
| `agriculture` | Agriculture |
| `health` | Health |
| `education` | Education |
| `water_sanitation` | Water & Sanitation |
| `infrastructure` | Infrastructure |
| `environment` | Environment |
| `mining` | Mining |
| `tribal_welfare` | Tribal Welfare |
| `employment` | Employment |
| `urban_development` | Urban Development |
| `energy` | Energy |

The classifier can also mark a challenge as:

```text
other
```

when the confidence is insufficient.

---

# AI Components

## Semantic Categorization

The semantic classifier uses:

```text
Sentence Transformers
all-MiniLM-L6-v2
```

The challenge is compared against semantic domain prototypes to determine the most relevant category.

Example:

```json
{
  "category": "agriculture",
  "confidence": 0.9809,
  "semantic_score": 0.XXXX,
  "margin": 0.XXXX,
  "uncertain": false
}
```

---

## Problem Extraction

The extraction module identifies important information from the challenge description:

- Problem
- Affected group
- Location
- Causes
- Impact

---

## Priority Scoring

The priority module calculates a priority score using factors including:

- Severity
- Affected population
- Urgency
- Impact
- Domain-specific considerations
- Risk adjustments

Example:

```json
{
  "score": 57,
  "level": "Medium"
}
```

---

## Similarity and Duplicate Detection

Similarity detection compares a new challenge with existing challenges.

The system uses:

```text
Sentence Transformers
all-MiniLM-L6-v2
```

The highest semantic similarity score is used to determine whether a challenge is:

- A duplicate
- Similar
- Not similar

Current thresholds:

```text
>= 0.95  -> Duplicate
>= 0.70  -> Similar
<  0.70  -> Not similar
```

Example:

```json
{
  "duplicate": false,
  "similar": true,
  "similarity_score": 0.7825,
  "matched_challenge": "Farmers in rural areas lack proper irrigation facilities."
}
```

---

## Image Analysis

Image analysis uses:

```text
OpenAI CLIP
openai/clip-vit-base-patch32
```

The model performs zero-shot classification against the supported societal domains.

---

## Audio Processing

Audio transcription uses:

```text
OpenAI Whisper
base model
```

Whisper runs locally as part of the Python service.

FFmpeg is required for audio processing.

---

## Multimodal Fusion

When multiple input types are provided, the service combines the available information.

For example:

```text
Text + Image + Audio
        |
        v
Unified Challenge Representation
        |
        v
AI Analysis Pipeline
```

The response identifies the sources used and creates a unified representation for downstream analysis.

---

# API

The service is implemented using:

```text
FastAPI
```

## Health Check

```http
GET /
```

Example response:

```json
{
  "message": "ai service running"
}
```

---

## Analyze Challenge

```http
POST /analyze
```

Accepts:

- Challenge text
- Optional image
- Optional audio

The endpoint runs the complete AI pipeline.

Example challenge:

```text
Farmers in rural villages are facing crop losses due to poor irrigation facilities.
```

Optional inputs:

```text
image
audio
```

The response contains:

```text
challenge
unified_text
category
extraction
priority
similarity
explanation
```

---

## Upload Image

```http
POST /upload-image
```

Processes an uploaded image and returns:

- Filename
- Content type
- File size
- Image information
- Image analysis

---

## Upload Audio

```http
POST /upload-audio
```

Processes an uploaded audio file and returns:

- Filename
- Content type
- File size
- Transcribed text

---

## Similarity Detection

```http
POST /similarity
```

Compares a submitted challenge against existing challenges.

It can also use image information as the semantic representation when an image is supplied.

Example response:

```json
{
  "duplicate": false,
  "similar": true,
  "similarity_score": 0.7825,
  "matched_challenge": "Farmers in rural areas lack proper irrigation facilities."
}
```

---

# Project Structure

```text
sih/
│
├── app/
│   │
│   ├── ai/
│   │   ├── explanation/
│   │   ├── extraction/
│   │   ├── fusion/
│   │   ├── multimodal/
│   │   ├── pipeline/
│   │   ├── priority/
│   │   ├── semantic/
│   │   └── similarity/
│   │
│   ├── processing/
│   │   ├── audio.py
│   │   ├── image.py
│   │   └── image_analysis.py
│   │
│   └── main.py
│
├── models/
├── tests/
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

# Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| API Framework | FastAPI |
| API Server | Uvicorn |
| Text Embeddings | Sentence Transformers |
| Text Model | `all-MiniLM-L6-v2` |
| Image Model | OpenAI CLIP |
| Image Processing | Pillow |
| Audio Transcription | OpenAI Whisper |
| Audio Dependency | FFmpeg |
| Numerical Processing | NumPy |
| ML Framework | PyTorch |
| Version Control | Git / GitHub |

---

# Local Setup

## 1. Clone the Repository

```bash
git clone <repository-url>
cd sih
```

---

## 2. Create Virtual Environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

---

## 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## 4. FFmpeg

FFmpeg is required for audio processing.

Verify that FFmpeg is available:

```powershell
ffmpeg -version
```

If FFmpeg is not available in the system PATH, add its `bin` directory to the PATH before starting the service.

---

# Running the Service

Start the development server:

```powershell
uvicorn app.main:app --reload
uvicorn app.main:app(production based)
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

# AI Model Initialization

Some AI models are downloaded the first time the service starts.

The first startup can therefore take significantly longer than subsequent requests.

After the models are available locally, requests are processed without downloading the models again for every request.

---

# Testing

The V1 service has been tested through the API for:

## Text Analysis

Verified:

- Challenge processing
- Categorization
- Problem extraction
- Priority calculation
- Similarity output
- Explanation generation

## Image Analysis

Verified:

- Image upload
- Image validation
- Image model execution
- API integration
- Multimodal pipeline execution

## Similarity Detection

Verified using semantically similar agricultural challenges.

## Audio

Audio transcription has been tested separately using Whisper.

---

# Current Limitations

V1 intentionally has a limited scope.

### Not Supported

- Video processing
- Video analysis
- Document processing

Video processing is reserved for V2.

---

# Security Status

The AI functionality of V1 is implemented.

Before public deployment, the service must undergo a dedicated security and production-hardening review covering:

- Input validation
- File upload limits
- Resource protection
- Rate limiting
- Authentication
- CORS
- Error handling
- Dependency security
- Temporary file handling
- Secret management
- Production configuration

The service should **not be considered fully production-secure until this review is completed.**

---

# Version Roadmap

## V1 — Current

```text
Text
Image
Audio
   |
   v
AI Analysis
   |
   v
Structured JSON
```

Focus:

> Reliable AI analysis of societal challenges.

---

## V2 — Planned

```text
Text
Image
Audio
Video
   |
   v
Multimodal AI Analysis
```

Video processing will be added in V2.

---

# Backend Integration

The Python service operates as an independent AI service.

The backend sends challenge information to the AI service and receives structured JSON.

Example:

```text
Backend
   |
   | Challenge + optional media
   v
Python AI Service
   |
   | AI Processing
   v
Structured JSON
   |
   v
Backend
```

The backend is responsible for the broader application workflow.

This repository is responsible for the **AI analysis layer**.

---

# Development Principle

The V1 implementation focuses on completing the required AI functionality without unnecessarily expanding the scope.

Future functionality should be introduced as separate versions where appropriate.

**V1 is focused on text, image, audio, and the core AI analysis pipeline.**

**Video is reserved for V2.**
