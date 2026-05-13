# PROJ-100 User Management & Authentication System

## Epic Description

Build a complete user management and authentication system for the SaaS platform. This epic covers user registration, login, role-based access control, and profile management. The system must integrate with the existing notification service for email verification and password resets.

## Stories

### PROJ-101 User Registration

**Description:** As a new user, I want to register an account with my email and password so that I can access the platform.

**Acceptance Criteria:**
- Given a valid email and password (8+ chars, 1 uppercase, 1 number), when I POST /api/v1/auth/register, then a 201 response is returned with my user ID
- Given an email that is already registered, when I POST /api/v1/auth/register, then a 409 Conflict response is returned
- Given an invalid email format, when I POST /api/v1/auth/register, then a 422 response with validation errors is returned
- Given a successful registration, when the user is created, then a verification email is sent via the notification service

**Story Points:** 5
**Priority:** High
**Labels:** auth, backend, api

---

### PROJ-102 Email Verification

**Description:** As a registered user, I want to verify my email address so that my account is fully activated.

**Acceptance Criteria:**
- Given a valid verification token, when I GET /api/v1/auth/verify?token=xxx, then my account is marked as verified and a 200 response is returned
- Given an expired verification token (> 24h), when I GET /api/v1/auth/verify?token=xxx, then a 410 Gone response is returned
- Given an unverified account, when I try to access protected endpoints, then a 403 response with "Email not verified" message is returned
- Given an expired token, when I POST /api/v1/auth/resend-verification, then a new verification email is sent

**Story Points:** 3
**Priority:** High
**Labels:** auth, backend, api

---

### PROJ-103 User Login & JWT Tokens

**Description:** As a verified user, I want to log in and receive a JWT token so that I can access protected endpoints.

**Acceptance Criteria:**
- Given valid credentials, when I POST /api/v1/auth/login, then a 200 response with access_token (15min TTL) and refresh_token (7d TTL) is returned
- Given invalid credentials, when I POST /api/v1/auth/login, then a 401 response is returned after a 500ms delay (timing attack prevention)
- Given a valid refresh_token, when I POST /api/v1/auth/refresh, then a new access_token is returned
- Given a revoked refresh_token, when I POST /api/v1/auth/refresh, then a 401 response is returned
- Given 5 failed login attempts, when I try to log in again, then the account is locked for 15 minutes

**Story Points:** 8
**Priority:** Critical
**Labels:** auth, security, backend, api

---

### PROJ-104 Role-Based Access Control (RBAC)

**Description:** As an admin, I want to assign roles to users so that I can control access to different parts of the system.

**Acceptance Criteria:**
- Given the roles: admin, manager, member, viewer, when a user is created, then they are assigned the "member" role by default
- Given an admin user, when they PUT /api/v1/users/{id}/role with a valid role, then the user's role is updated
- Given a non-admin user, when they try to change roles, then a 403 Forbidden response is returned
- Given a user with "viewer" role, when they try to POST/PUT/DELETE any resource, then a 403 response is returned
- Given the endpoint permission matrix, when any endpoint is accessed, then the middleware checks the user's role against the required permission

**Story Points:** 8
**Priority:** High
**Labels:** auth, security, backend, rbac

---

### PROJ-105 User Profile Management

**Description:** As an authenticated user, I want to view and update my profile so that I can manage my account information.

**Acceptance Criteria:**
- Given an authenticated user, when I GET /api/v1/users/me, then my profile (name, email, role, created_at, avatar_url) is returned
- Given an authenticated user, when I PATCH /api/v1/users/me with valid fields, then my profile is updated
- Given a PATCH request with email change, when the new email is submitted, then a verification email is sent to the new address
- Given a PATCH request with the current password and a new password, when submitted, then the password is changed and all other sessions are invalidated
- Given an authenticated user, when I DELETE /api/v1/users/me, then my account is soft-deleted and a 30-day recovery window starts

**Story Points:** 5
**Priority:** Medium
**Labels:** backend, api, user-management

---

## Technical Context

- **Language:** Python 3.12
- **Framework:** FastAPI with Pydantic v2
- **Database:** PostgreSQL 16 with SQLAlchemy 2.0 + Alembic migrations
- **Auth:** JWT via python-jose, passwords hashed with bcrypt (cost 12)
- **Cache:** Redis for rate limiting and token blacklist
- **Testing:** pytest + httpx for async tests
- **Deployment:** Docker container on AWS ECS
- **Existing Integration:** Notification service at `NOTIFICATION_SERVICE_URL` (accepts POST /send with `{"to": email, "template": name, "data": {}}`)

## Constraints

- Must be stateless (no server-side sessions) for horizontal scaling
- Must support the existing API gateway rate limit of 1000 req/min per IP
- Must comply with GDPR — user data export and deletion within 30 days
- All timestamps in UTC, stored as timestamptz in PostgreSQL
- API follows existing company convention: `/api/v1/` prefix, snake_case fields

## Out of Scope

- OAuth/SSO (planned for PROJ-200 epic, next quarter)
- Two-factor authentication (planned for PROJ-201)
- Frontend/UI (handled by frontend team, PROJ-150 epic)
- Admin dashboard (separate epic PROJ-180)
- Audit logging (separate epic PROJ-190)

## Definition of Done

- All acceptance criteria pass as automated tests
- API documentation auto-generated from OpenAPI schema
- Database migrations are reversible
- Docker image builds and runs locally
- README updated with setup and API usage instructions
