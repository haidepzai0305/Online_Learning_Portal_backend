# UniLearn Microservices Architecture & System Workflows

This document provides a comprehensive technical overview of the **UniLearn** Microservices Learning Portal backend. It maps out the architecture, the multi-database setup, asynchronous event-driven integrations, and core system workflows (including enrollment checkout and the AI-driven RAG study assistant).

---

## 🏛️ Microservices Architecture Overview

UniLearn is designed as a **modular Django monolith** acting as a set of logical microservices. Each service manages its own business logic, database models, and service interfaces, communicating asynchronously via a **RabbitMQ Topic Exchange**.

```mermaid
graph TD
    %% Styling
    classDef client fill:#e8f4fd,stroke:#1a73e8,stroke-width:2px;
    classDef gate fill:#fef7e0,stroke:#f9ab00,stroke-width:2px;
    classDef svc fill:#e6f4ea,stroke:#137333,stroke-width:2px;
    classDef db fill:#f3e8fd,stroke:#8a3ffc,stroke-width:2px;
    classDef broker fill:#fce8e6,stroke:#c5221f,stroke-width:2px;

    %% Nodes
    React[React Frontend<br>:5173]:::client
    DjangoGate[Django Gateway / Core URL Router<br>:8000]:::gate

    %% Services
    AuthSvc[Auth Service<br>myproject.auth_service]:::svc
    CourseSvc[Courses Service<br>myproject.courses_service]:::svc
    PaySvc[Payment Service<br>myproject.payment_service]:::svc
    NotiSvc[Notification Service<br>myproject.notification_service]:::svc
    AISvc[AI / RAG Service<br>myproject.ai_service]:::svc

    %% DB Router Routing
    AuthDb[(Auth DB<br>auth_db)]:::db
    CourseDb[(Course DB<br>course_db)]:::db
    PayDb[(Payment DB<br>payment_db)]:::db
    NotiDb[(Notification DB<br>notification_db)]:::db
    VectorStore[(In-Memory Vector Store<br>vector_store.json)]:::db

    %% Message Broker
    RMQ[RabbitMQ Exchange<br>unilearn_events]:::broker

    %% Connections
    React -->|HTTP Requests| DjangoGate
    DjangoGate -->|/api/auth/| AuthSvc
    DjangoGate -->|/api/courses/| CourseSvc
    DjangoGate -->|/api/payments/| PaySvc
    DjangoGate -->|/api/notifications/| NotiSvc
    DjangoGate -->|/api/ai/| AISvc

    %% Database Router mapping
    AuthSvc --> AuthDb
    CourseSvc --> CourseDb
    PaySvc --> PayDb
    NotiSvc --> NotiDb
    AISvc -.-> VectorStore

    %% RabbitMQ Events
    PaySvc -->|Publish payment.success / payment.failed| RMQ
    CourseSvc -->|Publish course_created / material_uploaded| RMQ
    RMQ -->|Consume payment.success| CourseSvc
    RMQ -->|Consume # all events| NotiSvc
```

### 💾 Multi-Database Routing
To isolate services at the database tier, UniLearn utilizes Django's `DatabaseRouter` (`config/db_router.py`), mapping database interactions dynamically based on Django `app_label`:
* **Auth Service** (`app`) ➔ `default` database (`auth_db` MySQL)
* **Courses Service** (`courses_service_app`) ➔ `courses` database (`course_db` MySQL)
* **Notification Service** (`notification_service_app`) ➔ `notifications` database (`notification_db` MySQL)
* **Payment Service** (`payment_service`) ➔ `payments` database (`payment_db` MySQL)

---

## 🔄 Core System Workflows

### 💳 1. Payment & Automated Enrollment Workflow (Event-Driven)
When a student purchases a course, the transaction flows asynchronously across three services, coordinated via RabbitMQ. This ensures high availability and fast user responses.

```mermaid
sequenceDiagram
    autonumber
    actor Student as Student (UI)
    participant PaySvc as Payment Service
    participant RMQ as RabbitMQ (unilearn_events)
    participant CourseSvc as Courses Service
    participant NotiSvc as Notification Service
    participant MailSvc as Django SMTP Mailer

    Student->>PaySvc: Initiate checkout (Course purchase)
    Note over PaySvc: Create Transaction (PENDING)
    PaySvc-->>Student: Return transaction info (Redirect/QR code)

    Student->>PaySvc: Complete payment simulation (confirm_payment)
    Note over PaySvc: Save Transaction as SUCCESS
    PaySvc->>RMQ: Publish event "payment.success"
    PaySvc-->>Student: Success HTTP 200

    par Course Worker Consumes "payment.success"
        RMQ-->>CourseSvc: Receive "payment.success" event
        Note over CourseSvc: CourseService.enroll_student(...)
        Note over CourseSvc: Create Enrollment entry in course_db
        CourseSvc->>MailSvc: Trigger enrollment confirmation email
        MailSvc-->>Student: Send Email: "Xác nhận thanh toán khóa học..."
    and Notification Worker Consumes "payment.success"
        RMQ-->>NotiSvc: Receive "payment.success" event (via # queue binding)
        Note over NotiSvc: Create notification "Thanh toán thành công 💳"
        Note over NotiSvc: Save in notification_db
    end
```

---

### 🧠 2. AI RAG Study Assistant Workflow (Retrieval-Augmented Generation)
The system leverages Google Gemini to answer questions using only indexed course files and includes clickable timestamps referencing exact video segments.

```mermaid
sequenceDiagram
    autonumber
    actor Prof as Professor
    actor Student as Student (UI)
    participant AISvc as AI / RAG Service
    participant Gemini as Google Gemini APIs
    participant CourseDb as Courses Service DB

    %% Document Indexing (Preparation)
    Prof->>AISvc: Upload Course Document (PDF, Slides, Video Transcript)
    Note over AISvc: Slide text into chunks (800-byte sliding window)
    loop For each text chunk
        AISvc->>Gemini: call gemini-embedding-001 (get 768-dim vector)
        Gemini-->>AISvc: Return Embedding vector
    end
    Note over AISvc: Store chunks, embeddings, metadata in vector_store.json

    %% Student Query (RAG Pipeline)
    Student->>AISvc: Ask course-related question (course_id, query)
    AISvc->>CourseDb: Fetch basic Course metadata (Title, Desc, Syllabus)
    CourseDb-->>AISvc: Return metadata
    AISvc->>Gemini: Get embedding for student's query text
    Gemini-->>AISvc: Return query vector
    Note over AISvc: Calculate similarity (manual dot-product) against indexed chunks
    Note over AISvc: Retrieve Top-K matching chunks & video timestamps metadata
    AISvc->>Gemini: Invoke gemini-2.5-flash with Prompt Guard + Context + Query
    Gemini-->>AISvc: Return structured Vietnamese study answer
    Note over AISvc: Append clickable video references if present
    AISvc-->>Student: Return final markdown response with video links
```

---

## ⚡ Technical Service Map

### A. Auth Service (`myproject/auth_service/`)
* **Database**: `auth_db`
* **Models**: `User` (Stores usernames, emails, salted passwords, and system roles: Student, Professor).
* **Capabilities**: Signs and verifies JWT security tokens using `python-jose` for user verification.

### B. Courses Service (`myproject/courses_service/`)
* **Database**: `course_db`
* **Models**: `Course`, `Material` (video_url, file), `Enrollment` (progress, course, student), `Announcement`, `Assignment`, `Submission`.
* **Capabilities**: Handles catalog creation, progress updates, enrollment registers, and triggers confirmation emails.

### C. Payment Service (`myproject/payment_service/`)
* **Database**: `payment_db`
* **Models**: `Transaction` (amount, payment_method, status: PENDING, SUCCESS, FAILED).
* **Capabilities**: Simulates payment collection and publishes event hooks to RabbitMQ.

### D. Notification Service (`myproject/notification_service/`)
* **Database**: `notification_db`
* **Models**: `Notification` (user_id, title, message, read status).
* **Capabilities**: Concurrently processes messages, creating alerts in the background.

### E. AI Service (`myproject/ai_service/`)
* **Storage**: `vector_store.json` (in-memory document matrix).
* **APIs**: Google Gemini REST APIs (`gemini-2.5-flash` for generation, `gemini-embedding-001` for embedding representation).
* **Capabilities**: Auto-indexes text, calculates vector similarity, and acts as a strict, course-scoped Q&A tutor.
