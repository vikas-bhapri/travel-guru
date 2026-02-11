# High Level Architecture

## Introduction

This document outlines the high-level architecture for a travel and tourism application. The system follows a microservices architecture pattern, with a Next.js frontend communicating through an API Gateway to various backend services. Each service is responsible for a specific domain and maintains its own data in a shared PostgreSQL database cluster.

### Flowchart

``` mermaid
flowchart TB
    User --> App[Next.JS UI]
    App --> API[API Gateway]
    API --> AuthMS[Auth Service]
    API --> BookMS[Booking Service]
    API --> InventoryMS[Inventory Service]
    API --> PaymentMS[Payment Service]
    API --> ReviewsMS[Reviews Service]
    AuthMS --> DB[PostgreSQL Server]
    BookMS --> DB[PostgreSQL Server]
    InventoryMS --> DB[PostgreSQL Server]
    PaymentMS --> DB[PostgreSQL Server]
    ReviewsMS --> DB[PostgreSQL Server]
```

### Kubernetes workflow

``` mermaid
flowchart TB
  classDef k8s fill:#f3f4f6,stroke:#6b7280,stroke-width:1px,color:#111;
  classDef svc fill:#eef7ff,stroke:#3b82f6,stroke-width:1px,color:#111;
  classDef data fill:#fff7e6,stroke:#f59e0b,stroke-width:1px,color:#111;
  classDef ext fill:#f0fdf4,stroke:#10b981,stroke-width:1px,color:#111;

  subgraph Cluster[Kubernetes Cluster]
    subgraph NS[Namespace: travel-app]
      IN[Ingress Controller]:::k8s

      subgraph FEDEP[Deployment: frontend]
        FE_P1[(Pod: Next.js)]:::svc
      end
      FESVC[Service: frontend]:::k8s

      subgraph APIDEP[Deployment: api-gateway]
        API_P1[(Pod: FastAPI BFF)]:::svc
        API_P2[(Pod: FastAPI BFF)]:::svc
      end
      APISVC[Service: api-gateway]:::k8s

      subgraph AUTHDEP[Deployment: auth-service]
        A1[(Pod: auth)]:::svc
        A2[(Pod: auth)]:::svc
      end
      AUTHSVC[Service: auth-service]:::k8s

      subgraph INVDEP[Deployment: inventory-service]
        I1[(Pod: inventory)]:::svc
      end
      INVSVC[Service: inventory-service]:::k8s

      subgraph BOOKDEP[Deployment: booking-service]
        B1[(Pod: booking)]:::svc
      end
      BOOKSVC[Service: booking-service]:::k8s

      subgraph PAYDEP[Deployment: payment-service]
        P1[(Pod: payment)]:::svc
      end
      PAYSVC[Service: payment-service]:::k8s

      subgraph REVDEP[Deployment: review-service]
        R1[(Pod: review)]:::svc
      end
      REVSVC[Service: review-service]:::k8s

      subgraph NOTIFDEP[Deployment: notification-service]
        N1[(Pod: notification)]:::svc
      end
      NOTIFSVC[Service: notification-service]:::k8s

      subgraph PGDEP[StatefulSet: postgresql]
        PG_P1[(Pod: postgres)]:::data
      end
      PGSVC[Service: postgres]:::k8s
      PGPVC[(PVC: pgdata)]:::data

      subgraph REDISDEP[Deployment: redis]
        RD1[(Pod: redis)]:::data
      end
      REDISSVC[Service: redis]:::k8s

      subgraph MQDEP[Deployment: message-broker]
        MQ1[(Pod: kafka/rabbitmq)]:::data
      end
      MQSVC[Service: message-broker]:::k8s

      %% Networking inside cluster
      IN --> FESVC
      IN --> APISVC
      FESVC --> FE_P1
      APISVC --> API_P1
      APISVC --> API_P2

      API_P1 --> AUTHSVC
      API_P1 --> INVSVC
      API_P1 --> BOOKSVC
      API_P1 --> PAYSVC
      API_P1 --> REVSVC
      API_P1 --> NOTIFSVC

      A1 --> PGSVC
      A2 --> PGSVC
      I1 --> PGSVC
      B1 --> PGSVC
      P1 --> PGSVC
      R1 --> PGSVC
      N1 --> PGSVC

      API_P1 --> REDISSVC
      A1 --> REDISSVC

      B1 --- MQSVC
      P1 --- MQSVC
      N1 --- MQSVC

      PG_P1 --- PGPVC
    end
  end

```
