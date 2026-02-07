# Smart Attendance System - Design Report

**Project:** Smart Attendance System
**Date:** February 5, 2026

---

## 1. Circuit Breaker Pattern (State Pattern)

### Design Overview
The Circuit Breaker pattern protects the system from cascading failures when external services become unavailable.

### Architecture
```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│ PDF Processing  │────►│  Circuit Breaker │────►│ Attendance Service │
│    Service      │     │   (3 States)     │     │     (External)     │
└─────────────────┘     └──────────────────┘     └────────────────────┘
```

### State Machine Design
```
         ┌──────────┐
         │  CLOSED  │◄─────────────────────┐
         └────┬─────┘                      │
              │ 3 failures                 │ 2 successes
              ▼                            │
         ┌──────────┐    15s timeout  ┌────┴─────┐
         │   OPEN   │────────────────►│ HALF_OPEN│
         └──────────┘                 └──────────┘
              ▲                            │
              │         failure            │
              └────────────────────────────┘
```

### Implementation Details
| Component | Description |
|-----------|-------------|
| **Location** | `common/circuit_breaker.py` (Manual), `common/circuit_breaker_library.py` (pybreaker) |
| **States** | CLOSED, OPEN, HALF_OPEN |
| **Failure Threshold** | 3 consecutive failures |
| **Reset Timeout** | 15 seconds |
| **Pattern Type** | State Pattern (Behavioral) |

### Two Implementations
1. **Manual Implementation** - Full control over state transitions and logging
2. **Library Implementation** - Using `pybreaker` library for proven reliability

---

## 2. Strategy Pattern

### Design Overview
The Strategy Pattern allows runtime selection of report generation algorithms without modifying client code.

### Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    ReportFormatStrategy                 │
│                     <<abstract>>                        │
├─────────────────────────────────────────────────────────┤
│ + generate_student_report(data): str                    │
│ + generate_course_report(data): str                     │
│ + get_format_name(): str                                │
│ + get_file_extension(): str                             │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ExcelStrategy  │ │ PDFStrategy   │ │ CSVStrategy   │
│    .xlsx      │ │    .pdf       │ │    .csv       │
└───────────────┘ └───────────────┘ └───────────────┘
```

### Implementation Details
| Component | Description |
|-----------|-------------|
| **Location** | `reporting-service/strategies/` |
| **Abstract Class** | `ReportFormatStrategy` |
| **Concrete Strategies** | Excel, PDF, CSV |
| **Factory** | `strategy_factory.py` (with Reflection) |
| **Configuration** | `config/report_config.yml` |

### Factory with Reflection
```python
# Dynamic strategy loading at runtime
strategy = strategy_factory.create_strategy("pdf")  # Returns PDFStrategy
strategy = strategy_factory.create_strategy("csv")  # Returns CSVStrategy
```

---

## 3. Choreography Pattern (Event-Driven)

### Design Overview
Services communicate through events via RabbitMQ message broker without a central coordinator.

### Architecture
```
┌────────────────────┐                      ┌────────────────────┐
│ Attendance Service │                      │   Course Service   │
│    (Producer)      │                      │    (Consumer)      │
└─────────┬──────────┘                      └──────────▲─────────┘
          │                                            │
          │  publish                          consume  │
          │                                            │
          ▼          ┌──────────────────┐              │
          └─────────►│    RabbitMQ      │──────────────┘
                     │ attendance_events│
                     │     (Queue)      │
                     └──────────────────┘
```

### Event Flow
```
1. Attendance recorded
         │
         ▼
2. Event published: {event: "attendance_recorded", student_id, course_id, date, status}
         │
         ▼
3. RabbitMQ queues the message
         │
         ▼
4. Course Service consumes event independently
         │
         ▼
5. Event processed and acknowledged
```

### Implementation Details
| Component | Description |
|-----------|-------------|
| **Message Broker** | RabbitMQ |
| **Client Location** | `common/rabbitmq_client.py` |
| **Producer** | `attendance-service/app.py` |
| **Consumer** | `course-service/app.py` |
| **Queue Name** | `attendance_events` |
| **Delivery Mode** | Persistent (durable) |

### Key Characteristics
- **Asynchronous**: Services don't wait for each other
- **Loose Coupling**: No direct service-to-service calls
- **Scalability**: Multiple consumers can process events
- **Reliability**: Messages persist until acknowledged

---

## 4. JWT Authentication

### Design Overview
Token-based authentication using JSON Web Tokens for secure, stateless authentication across microservices.

### Architecture
```
┌──────────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│ Frontend │────►│ API Gateway │────►│ Auth Service │     │   Services   │
│          │     │ (Validates) │     │ (Generates)  │     │              │
└──────────┘     └──────┬──────┘     └──────────────┘     └──────────────┘
                        │                                        ▲
                        │     X-User-ID, X-Username, X-Role      │
                        └────────────────────────────────────────┘
```

### Token Flow
```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. LOGIN                                                            │
│    User ──► POST /api/auth/login {username, password}               │
│         ◄── {token: "eyJ...", user: {...}}                          │
├─────────────────────────────────────────────────────────────────────┤
│ 2. STORE                                                            │
│    Frontend stores token in localStorage                            │
├─────────────────────────────────────────────────────────────────────┤
│ 3. REQUEST                                                          │
│    User ──► GET /api/attendance                                     │
│             Header: Authorization: Bearer eyJ...                    │
├─────────────────────────────────────────────────────────────────────┤
│ 4. VALIDATE                                                         │
│    API Gateway validates signature and expiration                   │
│    Extracts user_id, username, role                                 │
├─────────────────────────────────────────────────────────────────────┤
│ 5. FORWARD                                                          │
│    Request forwarded to service with user headers                   │
└─────────────────────────────────────────────────────────────────────┘
```

### JWT Token Structure
```
Header:    { "alg": "HS256", "typ": "JWT" }
Payload:   { "user_id": 1, "username": "admin", "role": "admin", "exp": ... }
Signature: HMACSHA256(base64(header) + "." + base64(payload), secret)
```

### Implementation Details
| Component | Description |
|-----------|-------------|
| **Auth Service** | `auth-service/app.py` (Port 5007) |
| **API Gateway** | `api-gateway/app.py` (Port 5000) |
| **Frontend Client** | `frontend/lib/api.ts` |
| **Algorithm** | HS256 |
| **Token Expiration** | 24 hours |
| **Library** | PyJWT |

### Security Features
- **Stateless**: No server-side session storage required
- **Signed**: Prevents token tampering
- **Expiration**: Automatic token invalidation
- **Role-Based**: Supports admin, teacher, student roles

---

## System Overview

```
                                    ┌─────────────────┐
                                    │    Frontend     │
                                    │   (Next.js)     │
                                    └────────┬────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         API Gateway (5000)                          │
│                      JWT Validation + Routing                       │
└──────────┬──────────────────┬──────────────────┬───────────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Auth Service    │ │ PDF Processing   │ │ Reporting Service│
│  (JWT - 5007)    │ │ (CB - 5004)      │ │ (Strategy - 5003)│
└──────────────────┘ └────────┬─────────┘ └──────────────────┘
                              │
                              │ Circuit Breaker
                              ▼
                    ┌──────────────────┐         ┌──────────────────┐
                    │Attendance Service│◄───────►│   RabbitMQ       │
                    │     (5005)       │ publish │ (Choreography)   │
                    └──────────────────┘         └────────┬─────────┘
                                                          │ consume
                                                          ▼
                                                ┌──────────────────┐
                                                │  Course Service  │
                                                │     (5002)       │
                                                └──────────────────┘
```

---

## Summary Table

| Pattern | Type | Purpose | Location |
|---------|------|---------|----------|
| Circuit Breaker | Behavioral (State) | Fault tolerance | `common/circuit_breaker.py` |
| Strategy | Behavioral | Algorithm selection | `reporting-service/strategies/` |
| Choreography | Architectural | Event-driven communication | `common/rabbitmq_client.py` |
| JWT Auth | Security | Stateless authentication | `auth-service/app.py` |

---

**End of Report**
