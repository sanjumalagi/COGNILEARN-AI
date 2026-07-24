# Infrastructure Setup
## CogniLearn AI

---

# Document Information

| Property | Value |
|----------|-------|
| Document Name | Infrastructure Setup |
| Version | 1.0 |
| Status | Approved Deployment Document |
| Purpose | Define the infrastructure requirements, server configuration, networking, security, containerization, and environment setup required for deploying CogniLearn AI in a production environment. |

---

# 1. Introduction

A robust infrastructure is essential for ensuring that CogniLearn AI operates reliably, securely, and efficiently in production. This document describes the hardware, operating system, networking, software dependencies, and deployment tools required to support the platform.

The infrastructure has been designed using modern deployment practices, emphasizing modularity, security, maintainability, and scalability.

---

# 2. Infrastructure Objectives

The infrastructure should:

- Provide reliable application hosting.
- Ensure secure communication.
- Support multiple concurrent users.
- Enable containerized deployment.
- Simplify future upgrades.
- Support monitoring and logging.
- Protect application data.
- Allow future cloud migration.

---

# 3. Infrastructure Overview

```
                    Internet
                        │
                        ▼
                 Domain Name (DNS)
                        │
                        ▼
                  HTTPS (SSL/TLS)
                        │
                        ▼
                 Nginx Reverse Proxy
                        │
        ┌───────────────┴───────────────┐
        ▼                               ▼
 React Frontend                  FastAPI Backend
                                        │
                    ┌───────────────────┴─────────────────┐
                    ▼                                     ▼
             PostgreSQL Database                  AI Service Layer
                                                          │
                                                          ▼
                                                  Google Gemini API
```

---

# 4. Hardware Requirements

### Minimum Requirements

| Resource | Specification |
|----------|---------------|
| CPU | 2 vCPUs |
| RAM | 4 GB |
| Storage | 40 GB SSD |
| Network | Stable Internet Connection |

---

### Recommended Production Requirements

| Resource | Specification |
|----------|---------------|
| CPU | 4–8 vCPUs |
| RAM | 8–16 GB |
| Storage | 100 GB SSD |
| Bandwidth | High-Speed Internet |
| Backup Storage | Separate Volume |

---

# 5. Operating System

Recommended operating systems:

- Ubuntu Server 24.04 LTS
- Ubuntu Server 22.04 LTS
- Debian 12
- Rocky Linux 9

Ubuntu LTS is recommended due to its stability, security updates, and extensive community support.

---

# 6. Required Software

| Software | Purpose |
|----------|---------|
| Docker | Containerization |
| Docker Compose | Multi-container orchestration |
| Nginx | Reverse Proxy |
| Git | Version Control |
| Python 3.11+ | Backend Runtime |
| Node.js 20+ | Frontend Build |
| PostgreSQL | Database |
| OpenSSL | SSL Management |
| Certbot | TLS Certificate Management |

---

# 7. Production Directory Structure

```
/opt/cognilearn/

│
├── backend/
├── frontend/
├── docker/
├── nginx/
├── logs/
├── backups/
├── ssl/
├── uploads/
├── scripts/
├── monitoring/
└── .env
```

This structure separates application code, configuration, logs, backups, and deployment resources.

---

# 8. Containerization Strategy

Each major component is deployed independently.

```
Docker Host

├── nginx
├── frontend
├── backend
├── postgres
└── monitoring
```

Benefits include:

- Isolation
- Simplified deployment
- Easier maintenance
- Consistent environments
- Independent scaling

---

# 9. Networking Configuration

Recommended network ports:

| Port | Purpose |
|------|---------|
| 80 | HTTP |
| 443 | HTTPS |
| 8000 | FastAPI (Internal) |
| 5432 | PostgreSQL (Internal) |

Only ports **80** and **443** should be publicly accessible. Internal services should remain protected behind the reverse proxy.

---

# 10. Reverse Proxy Configuration

Nginx serves as the reverse proxy.

Responsibilities include:

- HTTPS termination.
- Request routing.
- Static file serving.
- Load balancing (future).
- Compression.
- Security headers.
- Request logging.

All client traffic is routed through Nginx before reaching backend services.

---

# 11. Environment Configuration

Application settings are managed through environment variables.

Typical configuration includes:

- Database URL
- JWT secret
- AI API key
- AI model name
- Logging level
- Allowed origins
- SMTP configuration
- Feature flags

Secrets must never be hardcoded into the source code.

---

# 12. Database Setup

Production database:

- PostgreSQL

Recommended practices:

- Dedicated database user.
- Strong passwords.
- Daily backups.
- Restricted network access.
- Indexed tables.
- Regular maintenance.
- Connection pooling.

Persistent volumes should be used to prevent data loss.

---

# 13. SSL Configuration

All production traffic should use HTTPS.

SSL provides:

- Data encryption.
- Secure authentication.
- User privacy.
- Protection against interception.

Certificates can be managed using:

- Let's Encrypt
- Certbot

Automatic certificate renewal is recommended.

---

# 14. Firewall Configuration

Only essential ports should be open.

Example policy:

| Port | Access |
|------|--------|
| 22 | SSH (Restricted) |
| 80 | Public |
| 443 | Public |
| 5432 | Internal Only |
| 8000 | Internal Only |

Restricting unnecessary ports reduces the attack surface.

---

# 15. Secrets Management

Sensitive information includes:

- JWT secrets.
- AI API keys.
- Database passwords.
- SMTP credentials.
- Encryption keys.

Secrets should be:

- Stored securely.
- Rotated periodically.
- Accessible only to authorized services.
- Excluded from version control.

---

# 16. Storage Management

Persistent storage includes:

- Database files.
- Uploaded study materials.
- Application logs.
- Backup archives.
- SSL certificates.

Separate storage volumes improve reliability and simplify backup operations.

---

# 17. Monitoring Preparation

Infrastructure should expose metrics for:

- CPU utilization.
- Memory usage.
- Disk usage.
- Network activity.
- API response times.
- Database health.
- Container status.

These metrics support proactive maintenance.

---

# 18. Backup Preparation

Regular backups should include:

- PostgreSQL database.
- Uploaded files.
- Configuration files.
- SSL certificates.
- Environment variables.
- Deployment scripts.

Backups should be stored securely and verified through periodic restoration tests.

---

# 19. Infrastructure Security

Infrastructure security measures include:

- SSH key authentication.
- Strong passwords.
- Least privilege access.
- Automatic security updates.
- Firewall rules.
- HTTPS enforcement.
- Container isolation.
- Regular vulnerability scanning.

Security should be maintained throughout the operational lifecycle.

---

# 20. Infrastructure Validation Checklist

Before deployment, verify:

- Operating system updated.
- Docker installed.
- Docker Compose installed.
- PostgreSQL configured.
- Nginx configured.
- SSL certificates installed.
- Firewall enabled.
- Environment variables configured.
- Domain configured.
- Monitoring enabled.
- Backup system tested.
- Secrets securely stored.

---

# 21. Relationship with Previous Phases

| Development Phase | Contribution |
|-------------------|--------------|
| System Architecture | Logical design |
| Software Design | Component structure |
| Implementation Guide | Application implementation |
| Testing & Validation | Verified correctness |
| Infrastructure Setup | Production environment preparation |

Infrastructure setup provides the operational foundation for the validated application.

---

# 22. Future Enhancements

Future infrastructure improvements may include:

- Kubernetes clusters.
- Managed PostgreSQL services.
- Redis caching.
- Object storage integration.
- Infrastructure as Code (Terraform).
- Multi-region deployment.
- Auto-scaling groups.
- Service mesh technologies.

These enhancements support increased scalability, resilience, and operational efficiency.

---

# 23. Summary

This document defined the infrastructure required to deploy CogniLearn AI in a production environment. It covered hardware and software requirements, networking, containerization, storage, database configuration, SSL, security, monitoring, backups, and operational readiness.

The proposed infrastructure emphasizes reliability, security, modularity, and maintainability while providing a scalable foundation for future growth and cloud deployment.

---

# Guiding Principles

> Infrastructure should provide a secure and reliable foundation for educational services.

> Production environments should be isolated from development and testing environments.

> Sensitive information must be managed securely and never embedded within application code.

> Containerization improves portability, consistency, and maintainability.

> Infrastructure should be designed for future scalability and operational resilience.

> Educational Intelligence should remain independent of AI-generated instructional content regardless of deployment environment.

> Educational Intelligence drives Teaching Intelligence.

---

**End of Document**