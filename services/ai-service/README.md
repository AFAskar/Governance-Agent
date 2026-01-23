# Compliance Framework Evaluation System

AI service for extracting compliance controls from framework documents and evaluating applicant documents against those frameworks.

## Directory Structure

### Input Directories (Place your PDFs here)

```
data/
├── inputs/
│   ├── frameworks/          # Place framework PDF files here
│   └── applicants/         # Place applicant PDF files here
```

**Usage:**
- **Framework PDFs**: Place compliance framework PDFs in `data/inputs/frameworks/`
- **Applicant PDFs**: Place applicant documents to evaluate in `data/inputs/applicants/`

### Output Directories (Generated automatically)

```
config/
├── frameworks/             # Framework outputs (controls.json, evaluation_prompt.txt)
│   └── {framework_name}/
│       ├── controls.json
│       └── evaluation_prompt.txt
└── vector_db/             # Qdrant vector database storage

data/
└── outputs/
    └── evaluations/        # Evaluation reports (JSON files)
```

**What gets saved where:**
- **Framework Data**: `config/frameworks/{framework_name}/`
  - `controls.json` - Extracted compliance controls
  - `evaluation_prompt.txt` - Generated evaluation prompt
  
- **Evaluation Reports**: `data/outputs/evaluations/`
  - Format: `{framework_name}_{applicant_name}_{timestamp}.json`
  
- **Vector Database**: `config/vector_db/` (Qdrant local storage)

## Quick Start

### 1. Setup a Framework

```python
from main import setup_framework

# Place your framework PDF in data/inputs/frameworks/
setup_framework(
    'data/inputs/frameworks/my_framework.pdf',
    'my_framework'
)
```

This will:
- Extract controls from the PDF
- Generate an evaluation prompt
- Save everything to `config/frameworks/my_framework/`

### 2. Index Framework Documents (Optional)

```python
from main import index_framework_documents

# Index framework for vector search
index_framework_documents(
    'data/inputs/frameworks/my_framework.pdf',
    'my_framework'
)
```

### 3. Evaluate Applicant Documents

```python
from main import evaluate_applicant_documents

# Place applicant PDFs in data/inputs/applicants/
evaluate_applicant_documents(
    ['data/inputs/applicants/applicant1.pdf'],
    'my_framework',
    applicant_name='applicant1'
)
```

The evaluation report will be saved to `data/outputs/evaluations/`

## Future API Integration

When you build the API later, you can:

1. **Upload endpoints**:
   - `POST /api/frameworks/upload` → Save to `data/inputs/frameworks/`
   - `POST /api/applicants/upload` → Save to `data/inputs/applicants/`

2. **Processing endpoints**:
   - `POST /api/frameworks/process` → Run `setup_framework()`
   - `POST /api/evaluations/create` → Run `evaluate_applicant_documents()`

3. **Retrieval endpoints**:
   - `GET /api/frameworks` → List from `config/frameworks/`
   - `GET /api/evaluations/{id}` → Load from `data/outputs/evaluations/`

## Notes

- All data directories are in `.gitignore` (user uploads and generated content)
- The directory structure is designed to be API-friendly
- Paths are relative to the project root (`services/ai-service/`)
