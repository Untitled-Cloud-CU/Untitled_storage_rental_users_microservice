
# 🚀 Storage Rental – Users Microservice

**Cloud Run • Cloud SQL • FastAPI • SQLAlchemy • ETags • Async Jobs • Docker**

Microservice for managing user accounts, authentication, and user-related operations in the Storage Rental application.
This service is responsible for **user identity, CRUD operations, rental associations**, and provides **robust RESTful functionality** including pagination, ETags, async processing, and linked-data responses.

---

# 📌 Overview

The Storage Rental system is composed of multiple microservices—Users, Locations, and Products—plus a composite microservice and a web UI.
The **Users Microservice** provides a clean REST API for:

* Managing users and user profiles
* Fetching user rental history
* Email verification via async workflows
* Supporting the composite microservice
* Powering the frontend sign-in/sign-up flows

This microservice evolved significantly between **Sprint 1** and **Sprint 2**.

---

# 🟦 Sprint 1 Summary — What Was Completed

During Sprint 1, the goal was to define the full structure of the service without implementing business logic. We built the following:

### ✅ 1. Full REST API skeleton

All required endpoints defined using FastAPI:

* GET /users
* GET /users/{id}
* POST /users
* PUT /users/{id}
* DELETE /users/{id}
* Authentication endpoints (register/login stubs)
* Rental history endpoints (stubbed)
* Health + root endpoints

### ✅ 2. Pydantic models created

* UserBase, UserCreate, UserUpdate
* Rental models
* TaskStatus (for async work, stubbed)

### ✅ 3. OpenAPI auto-documentation

Swagger UI available at:

```
/docs
```

### ✅ 4. NOT IMPLEMENTED placeholder responses

The skeleton returned consistent placeholder JSON so the frontend could begin integrating.

### ✅ 5. CORS middleware configured

Allowed communication from local frontend and composite service.

### ✍️ Sprint 1 Goal Achieved

A **complete structural API** ready for database integration and real business logic.

---

# 🟩 Sprint 2 Summary — What We Completed

Sprint 2 required turning the skeleton into a **fully functional, deployed cloud microservice**.
Here is everything we successfully built:

---

## ✔️ **1. Real MySQL Database Integration (Cloud SQL)**

* Connected the microservice to a **Cloud SQL MySQL instance**
* Implemented SQLAlchemy ORM models
* Added full create/update/delete persistence
* Enforced **unique email constraint**
* Implemented Unix-socket Cloud Run DB connection

---

## ✔️ **2. CRUD Operations Fully Implemented**

All core endpoints now write to the real database:

* **POST** `/users` → inserts user, returns **201 Created**
* **GET** `/users` → returns paginated + filtered results
* **GET** `/users/{id}` → fetches DB record
* **PUT** `/users/{id}` → updates DB, regenerates ETag
* **DELETE** `/users/{id}` → removes user

---

## ✔️ **3. ETag Support (Required Feature)**

Implemented on both GET and PUT:

### GET users/{id}

* Returns `ETag: <hash>`
* If client sends `If-None-Match`, server responds:

  * `304 Not Modified`

### PUT users/{id}

* Client must send `If-Match`
* If ETag mismatches:

  * `412 Precondition Failed`

---

## ✔️ **4. Pagination & Query Parameters**

`GET /users?skip=0&limit=10&city=Boston&status=active`

* Supports filtering by `city`, `state`, `status`
* Mandatory pagination (`skip`, `limit`)
* Matches backend requirements

---

## ✔️ **5. Linked Data + Relative Paths (HATEOAS)**

Every user response now includes:

```json
"_links": {
  "self": "/api/v1/users/5",
  "rentals": "/api/v1/users/5/rentals",
  "verify_email": "/api/v1/users/verify-email"
}
```

---

## ✔️ **6. 202 Accepted + Async Job + Polling**

Requirement fulfilled via:

### POST `/users/verify-email`

→ returns **202 Accepted**
→ body includes `task_id` + poll link:

```json
{
  "task_id": "abc123",
  "status": "accepted",
  "_links": {
    "poll": "/api/v1/users/jobs/abc123"
  }
}
```

### GET `/users/jobs/{task_id}`

→ returns status progression:
`accepted → processing → completed`

---

## ✔️ **7. Full Cloud Deployment**

### Built using:

* Cloud Build
* Artifact Registry

### Deployed to:

* **Cloud Run**
* Connected to Cloud SQL via unix socket

### Final service URL:

```
https://users-service-xxxxxx-uc.a.run.app
```

---

## ✔️ **8. Dockerized & Cloud-Ready**

* Multi-stage Dockerfile
* Production-ready Gunicorn/Uvicorn server
* Cloud Run compatible

---

# 🧰 API Endpoints (Sprint 2 Final)

## 👥 Users

| Method | Endpoint                  | Description                                |
| ------ | ------------------------- | ------------------------------------------ |
| GET    | `/api/v1/users/`          | Paginated user list with filtering + links |
| GET    | `/api/v1/users/{user_id}` | Returns user + ETag                        |
| POST   | `/api/v1/users/`          | Create user (**201 Created**)              |
| PUT    | `/api/v1/users/{user_id}` | Update user (**ETag required**)            |
| DELETE | `/api/v1/users/{user_id}` | Delete user                                |

## 🔐 Authentication (structure available)

| POST | `/api/v1/users/register` |
| POST | `/api/v1/users/login` |

## 🔄 Async Jobs

| POST | `/api/v1/users/verify-email` | 202 accepted |
| GET | `/api/v1/users/jobs/{task_id}` | Poll |

## 🏥 System

| GET | `/health` |
| GET | `/` |

---

# 🏗️ Architecture

```
Cloud Run (Users Service)
        |
        |—> Cloud SQL (MySQL)
        |
        |—> Composite Microservice
        |
        |—> Frontend (Cloud Storage Hosting)
```

---

# 🚀 Local Development

```bash
uvicorn app.main:app --reload
```

Swagger Docs:

```
http://localhost:8000/docs
```

---

# 🧪 Testing

Use Swagger, Postman, or curl:

```bash
curl https://users-service.../api/v1/users/
```

---

# 👥 Team

* **Sahasra** – Users Microservice
* **Molly** – Composite + Frontend Integration

---

# 🎉 Status

### **Sprint 1 ✔ Completed**

### **Sprint 2 ✔ Completed and fully deployed**

### Users Microservice meets ALL required specifications.

---
