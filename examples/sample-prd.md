# Product Requirements Document: Task Management API

## Overview
Build a REST API for a task management application. Users can create accounts, manage projects, and track tasks within projects.

## Target Users
- Software development teams (5-20 members)
- Project managers who need task visibility

## Functional Requirements

### Authentication
- Users can register with email and password
- Users can log in and receive a JWT token
- Users can reset their password via email
- Tokens expire after 24 hours with refresh token support

### Projects
- Users can create, read, update, and delete projects
- Projects have a name, description, and status (active/archived)
- Project owners can invite other users as members
- Members can have roles: owner, admin, member, viewer

### Tasks
- Users can create tasks within a project
- Tasks have: title, description, status, priority, assignee, due date
- Task statuses: todo, in-progress, in-review, done
- Task priorities: low, medium, high, critical
- Tasks can have comments
- Tasks can be assigned to project members
- Tasks can have labels/tags

### Activity Feed
- All changes to tasks and projects are logged
- Users can view activity feed per project
- Activity includes: who, what, when

## Non-Functional Requirements

### Performance
- API response time < 200ms for 95th percentile
- Support 100 concurrent users
- Database queries < 50ms

### Security
- Passwords hashed with bcrypt (cost factor 12)
- All endpoints require authentication (except register/login)
- Rate limiting: 100 requests per minute per user
- Input validation on all endpoints

### Scalability
- Stateless API (horizontal scaling ready)
- Database connection pooling

### Technology Preferences
- Node.js with TypeScript
- PostgreSQL database
- Express.js framework
- Prisma ORM
- Jest for testing

## Out of Scope
- Frontend/UI
- Real-time notifications (WebSocket)
- File attachments
- Mobile app
