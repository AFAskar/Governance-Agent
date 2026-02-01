# QUICK REFERENCE: Evaluation Agent System

---

## 🎯 System Summary (One Page)

### What You're Building
```
Multi-File Compliance Evaluation Agent
├── Frontend: 15 file upload fields
├── Backend: FastAPI + Celery task queue
├── Agent: LangGraph-based evaluation workflow
├── RAG: Qdrant vector DB for framework controls
├── LLM: Qwen2.5-32B (local) + Claude-3.5-Sonnet (API testing)
└── Output: Comprehensive compliance reports (JSON + PDF)
```

---

## 📊 Technology Stack Comparison

### Recommended Stack (Final Choice)

| Component | Technology | Alternatives Considered | Why Chosen |
|-----------|-----------|------------------------|------------|
| **Frontend** | Next.js 14 + shadcn/ui | React, Vue, Svelte | Modern, fast, great DX, TypeScript |
| **Backend** | FastAPI | Django, Flask | Async, fast, great with ML, type hints |
| **Task Queue** | Celery + Redis | RQ, Dramatiq, Bull | Industry standard, reliable, scalable |
| **Agent Framework** | LangGraph | LangChain, CrewAI | Explicit state, checkpointing, debuggable |
| **LLM (Local)** | Qwen2.5-32B-Instruct | Mistral-Nemo-12B, Llama-3.1-70B | **Best Arabic**, 32K context, 32B size |
| **LLM (API Test)** | Claude-3.5-Sonnet | GPT-4o, Mistral Large | Best reasoning, 200K context, documents |
| **Vector DB** | Qdrant | Weaviate, Milvus, Chroma | Fast, local, filtering, open source |
| **Embeddings** | multilingual-e5-large | jina-v3, bge-m3 | 1024-dim, Arabic, instruction-tuned |
| **File Storage** | MinIO | AWS S3, local FS | S3-compatible, self-hosted, reliable |
| **Database** | PostgreSQL 15+ | MySQL, MongoDB | Reliable, JSONB support, battle-tested |
| **Cache** | Redis 7+ | Memcached | Fast, simple, pub/sub, widely used |
| **LLM Serving** | vLLM | Ollama, TGI | **Fastest inference**, optimized, batching |
| **Containers** | Docker Compose | Kubernetes, bare metal | Simple, reproducible, easy local dev |

---

## 🤖 LLM Selection (CRITICAL DECISION)

### Production (Local Deployment)

**RECOMMENDED: Qwen2.5-32B-Instruct** ⭐⭐⭐⭐⭐

```
Provider:      Alibaba Cloud
Parameters:    32B (manageable size)
Context:       32,768 tokens
Arabic:        ⭐⭐⭐⭐⭐ Native support, trained on 18% Arabic data
Languages:     29 languages (multilingual)
Performance:   Competitive with GPT-4 on benchmarks
Deployment:    vLLM (recommended) or Ollama
Hardware:      2x RTX 4090 (48GB) OR 1x A100 40GB
Inference:     ~50 tokens/sec (vLLM optimized)
License:       Apache 2.0 (commercial use OK)
Cost:          $0 (self-hosted)

Why chosen:
✅ Best Arabic support (native, not just multilingual)
✅ Perfect size (32B = manageable hardware)
✅ Large context (32K = handles long documents)
✅ Production-grade reliability
✅ Open source, permissive license
✅ Active development & community
```

**Alternative: Mistral-Nemo-12B-Instruct** (If hardware limited)

```
Parameters:    12B (lighter)
Context:       128K tokens (HUGE!)
Arabic:        ⭐⭐⭐ Decent (multilingual)
Hardware:      1x RTX 4090 (24GB)
Inference:     ~80 tokens/sec
License:       Apache 2.0

Why alternative:
✓ Lighter hardware requirements
✓ Massive context window
✓ Faster inference
✗ Weaker Arabic than Qwen
```

### Testing/Development (API)

**RECOMMENDED: Claude-3.5-Sonnet** ⭐⭐⭐⭐⭐

```
Provider:      Anthropic
Context:       200K tokens
Arabic:        ⭐⭐⭐⭐ Very good
Reasoning:     ⭐⭐⭐⭐⭐ Best-in-class
Documents:     ⭐⭐⭐⭐⭐ Excellent
Cost:          $3/$15 per 1M tokens (input/output)
Latency:       ~3-5 seconds per evaluation

Why for testing:
✅ Best reasoning & document understanding
✅ Huge context (fits all framework info)
✅ Fast development iteration
✅ Reliable output format
✅ No hardware setup needed
```

**Alternative: GPT-4o**

```
Context:       128K tokens
Arabic:        ⭐⭐⭐⭐ Very good
Cost:          $2.50/$10 per 1M tokens

Why alternative:
✓ Slightly cheaper
✓ Widely used
✗ Less consistent than Claude for structured outputs
```

---

## 🏗️ Architecture Overview

### System Layers

```
┌─────────────────────────────────────────┐
│          FRONTEND (Next.js)             │
│  - 15 file upload fields                │
│  - Progress tracking                    │
│  - Report dashboard                     │
└──────────────┬──────────────────────────┘
               │ HTTP/REST
┌──────────────┴──────────────────────────┐
│         BACKEND API (FastAPI)           │
│  - File validation                      │
│  - Task management                      │
│  - Authentication                       │
└──────────────┬──────────────────────────┘
               │ Celery Tasks
┌──────────────┴──────────────────────────┐
│      EVALUATION AGENT (LangGraph)       │
│  ┌─────────────────────────────────┐   │
│  │  Graph Workflow (Cyclic)        │   │
│  │  ┌─────────────────────────┐    │   │
│  │  │ File Processing Node    │    │   │
│  │  └─────────┬───────────────┘    │   │
│  │            ↓                     │   │
│  │  ┌─────────────────────────┐    │   │
│  │  │ RAG Retrieval Node      │    │   │
│  │  └─────────┬───────────────┘    │   │
│  │            ↓                     │   │
│  │  ┌─────────────────────────┐    │   │
│  │  │ Tool Execution Node     │    │   │
│  │  └─────────┬───────────────┘    │   │
│  │            ↓                     │   │
│  │  ┌─────────────────────────┐    │   │
│  │  │ LLM Evaluation Node     │    │   │
│  │  └─────────┬───────────────┘    │   │
│  │            ↓                     │   │
│  │     [Loop for next file]        │   │
│  │            ↓                     │   │
│  │  ┌─────────────────────────┐    │   │
│  │  │ Aggregation Node        │    │   │
│  │  └─────────┬───────────────┘    │   │
│  │            ↓                     │   │
│  │  ┌─────────────────────────┐    │   │
│  │  │ Report Generation Node  │    │   │
│  │  └─────────────────────────┘    │   │
│  └─────────────────────────────────┘   │
└──────────────┬──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│         STORAGE LAYER                   │
│  - Qdrant (vector DB)                   │
│  - MinIO (file storage)                 │
│  - PostgreSQL (results)                 │
│  - Redis (cache/queue)                  │
└──────────────┬──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│         LLM LAYER                       │
│  - Qwen2.5-32B (vLLM server)            │
│  - Claude API (testing)                 │
└─────────────────────────────────────────┘
```

---

## 🔄 Evaluation Workflow (Step-by-Step)

### Complete Flow

```
1. USER SUBMITS
   └─ 15 files uploaded with control mappings

2. VALIDATION
   ├─ Check file types (CSV, PPTX, DOCX, PDF, XLSX)
   ├─ Check file sizes (< 50MB each)
   └─ Validate control IDs

3. STORAGE
   ├─ Save files to MinIO
   ├─ Create DB record (PostgreSQL)
   └─ Enqueue Celery task

4. AGENT START
   ├─ Initialize LangGraph state
   └─ Load application data

5. FILE LOOP (x15 files)
   For each file:
   
   A. LOAD FILE
      └─ Download from MinIO, extract text/data
   
   B. RAG RETRIEVAL
      ├─ Get control IDs for this file
      ├─ Query Qdrant for control details
      └─ Assemble framework context
   
   C. TOOL SELECTION
      └─ LLM decides: data validator, calculator, extractor, etc.
   
   D. TOOL EXECUTION
      └─ Run tools, gather outputs
   
   E. LLM EVALUATION
      ├─ Combine: file + controls + tool outputs
      ├─ Call LLM (Qwen or Claude)
      └─ Get structured assessment
   
   F. SAVE RESULT
      └─ Update state, mark file complete
   
   Time per file: 10-25 seconds

6. AGGREGATION
   ├─ Combine all 15 evaluations
   ├─ Calculate overall score
   ├─ Find cross-file gaps
   └─ Generate recommendations
   
   Time: 10-20 seconds

7. REPORT
   ├─ Create structured JSON
   ├─ Generate PDF
   └─ Save to database
   
   Time: 10-20 seconds

8. NOTIFY
   └─ Update dashboard, send email

TOTAL TIME: 1.5-3 minutes (parallel processing)
```

---

## 🛠️ Tools Available to Agent

### Tool Set

```
1. DATA VALIDATOR (for CSV/XLSX)
   - Validates schema, data types, ranges
   - Returns: compliance status + issues
   
2. CALCULATOR
   - Computes metrics from data
   - Returns: calculated values
   
3. CONTENT EXTRACTOR
   - Extracts specific sections from documents
   - Returns: relevant text excerpts
   
4. FORMAT CHECKER
   - Verifies document structure
   - Returns: format compliance status
```

---

## 📊 Performance Metrics

### Per-File Evaluation

```
File load:          2-5 seconds
Text extraction:    1-3 seconds
RAG retrieval:      0.5-1 second
Tool execution:     1-5 seconds
LLM evaluation:     5-10 seconds (local) / 3-5 seconds (API)
Save result:        0.5 second

TOTAL PER FILE:     10-25 seconds
```

### Full Application (15 files)

```
Sequential:         150-375 seconds (2.5-6 minutes)
Parallel (3 files): 50-125 seconds (1-2 minutes)

Aggregation:        10-20 seconds
Report generation:  10-20 seconds

TOTAL END-TO-END:   1.5-3 minutes (parallel)
                    3-7 minutes (sequential)
```

### Scaling

```
Single GPU:         2-3 concurrent applications
Multiple GPUs:      Linear scaling
API mode:           10-20 concurrent (rate limits)
```

---

## 💰 Cost Analysis

### Hardware (One-time)

```
Option 1: 2x RTX 4090 (48GB total)
Cost:     ~$3,500
Suitable: Qwen2.5-32B

Option 2: 1x A100 40GB
Cost:     ~$10,000
Suitable: Qwen2.5-32B

Option 3: 1x RTX 4090 (24GB)
Cost:     ~$1,800
Suitable: Mistral-Nemo-12B (lighter model)
```

### Operational (Per Application)

```
Local LLM:
- Compute:      $0 (owned hardware)
- Electricity:  ~$0.10 (15 minutes @ 600W)
- Total:        ~$0.10

API (Testing):
- Claude:       ~$0.50 per application
- GPT-4o:       ~$0.30 per application
```

### Annual (1000 applications)

```
Local:          $100 (electricity only)
API:            $500 (Claude) or $300 (GPT-4o)

ROI: Hardware pays for itself in 7-10 months if doing 1000+ evaluations/year
```

---

## 🔐 Security & Compliance

### Data Security

```
✓ Files encrypted at rest (MinIO encryption)
✓ Files encrypted in transit (TLS)
✓ Local LLM processing (no data sent externally)
✓ Access control (JWT + RBAC)
✓ Audit logs (all evaluations tracked)
✓ File sandboxing (isolated processing)
✓ Virus scanning (ClamAV integration)
```

### Compliance Features

```
✓ GDPR-compliant (data retention policies)
✓ Audit trail (who, what, when)
✓ Deterministic evaluation (reproducible results)
✓ Explainable AI (evidence-based assessments)
✓ Client control (on-premises deployment)
```

---

## 🚀 Implementation Roadmap

### 12-Week Plan

```
Weeks 1-2:   Backend API + Storage
Weeks 3-4:   RAG System (Qdrant + embeddings)
Weeks 5-7:   Agent Implementation (LangGraph)
Weeks 8-9:   LLM Integration (Qwen + vLLM)
Week 10:     Report Generation
Weeks 11-12: Testing & Refinement
```

### MVP Scope

```
✓ 15 file upload fields
✓ File type validation
✓ Basic agent workflow (all nodes)
✓ RAG retrieval
✓ 4 core tools
✓ LLM evaluation (API first, then local)
✓ JSON report
✓ Basic dashboard
```

### Phase 2 Features

```
- PDF report generation
- Email notifications
- Advanced analytics dashboard
- Batch applications
- Admin panel
- Multi-framework support
```

---

## ✅ Critical Success Factors

### Must-Have

1. **Reliable LLM inference**
   - vLLM for performance
   - Fallback to API if local fails
   - Timeout handling

2. **State management**
   - LangGraph checkpointing
   - Resume from failure
   - Progress tracking

3. **Validation layers**
   - Input validation (files)
   - Output validation (LLM responses)
   - Data validation (schemas)

4. **Error handling**
   - Retry logic (3 attempts)
   - Graceful degradation
   - Clear error messages

5. **Monitoring**
   - Evaluation progress
   - LLM performance
   - System health

---

## ❓ Decision Points

### Before Starting Implementation

1. **Hardware budget?**
   - $1,800 (1x 4090) → Use Mistral-Nemo-12B
   - $3,500 (2x 4090) → Use Qwen2.5-32B ⭐ Recommended
   - $10,000 (A100) → Use Qwen2.5-32B or Command-R+

2. **Arabic priority?**
   - Critical → Use Qwen2.5-32B ⭐
   - Nice-to-have → Mistral-Nemo-12B OK

3. **Deployment timeline?**
   - <8 weeks → Start with API (Claude), migrate to local
   - >8 weeks → Build local from start

4. **Expected load?**
   - <10/day → Single GPU fine
   - >50/day → Plan for multiple GPUs

5. **Client requirements?**
   - On-premises only → Local LLM mandatory
   - Cloud OK → Consider hybrid (local + API fallback)

---

## 🎯 SUMMARY

### What You Have

✅ **Complete system design** (Frontend → Backend → Agent → Storage → LLM)
✅ **Technology stack recommendation** (FastAPI, LangGraph, Qwen2.5-32B, Qdrant)
✅ **Detailed agent architecture** (Graph-based, 6 nodes, state management)
✅ **LLM selection** (Qwen2.5-32B for local, Claude for API)
✅ **Performance expectations** (1.5-3 minutes per application)
✅ **Implementation roadmap** (12 weeks to production)
✅ **Cost analysis** (Hardware + operational)
✅ **Security considerations** (Encryption, local processing, audit)

### Key Decisions Made

1. **Agent Framework**: LangGraph (over LangChain)
2. **Local LLM**: Qwen2.5-32B-Instruct (best Arabic + size)
3. **API LLM**: Claude-3.5-Sonnet (best reasoning + documents)
4. **Vector DB**: Qdrant (fast, local, filtering)
5. **Backend**: FastAPI + Celery (async, scalable)

### Next Steps

1. Review this design document
2. Confirm hardware budget
3. Confirm Arabic priority level
4. Approve technology choices
5. Begin Phase 1 implementation (Backend API)

---

**You're ready to build!** 🚀

Detailed design document: `Evaluation_Agent_System_Design.md` (15,000+ words)