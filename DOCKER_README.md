# CapeControl - Production-Ready FastAPI Application

[![Docker Pulls](https://img.shields.io/docker/pulls/stinkie/capecraft)](https://hub.docker.com/r/stinkie/capecraft)
[![Docker Image Size](https://img.shields.io/docker/image-size/stinkie/capecraft/latest)](https://hub.docker.com/r/stinkie/capecraft)
[![Production Status](https://img.shields.io/badge/Production-Ready-green)](https://cape-control.com)

A production-ready FastAPI backend with React frontend, featuring comprehensive authentication, CSRF protection, and enterprise-grade security.

## 🚀 Live Demo

**Production Application**: https://cape-control.com

## 🐳 Quick Start

```bash
## Pull and run the latest image
docker run -d -p 8000:8000 stinkie/capecraft:latest

## Run with environment variables
docker run -d -p 8000:8000 \
  -e ENV=prod \
  -e DEBUG=false \
  -e DATABASE_URL=your_db_url \
  stinkie/capecraft:production-ready
```text
## 🔒 Security Features

- **CSRF Protection**: Token-based validation on all state-changing operations
- **JWT Authentication**: Secure token-based authentication system
- **Input Validation**: Pydantic models with comprehensive data validation
- **reCAPTCHA Integration**: Bot protection for user registration
- **Production Hardening**: Non-root user, health checks, minimal attack surface

## 📋 Available Tags

- `latest` - Latest stable production build
- `v1.0.0` - Specific version release
- `production-ready` - Production-optimized build

## 🛠️ Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENV` | Environment mode | `prod` |
| `DEBUG` | Debug mode | `false` |
| `PORT` | Application port | `8000` |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `JWT_SECRET` | JWT token secret | Required |
| `DISABLE_RECAPTCHA` | Disable reCAPTCHA | `false` |

## 🏗️ Architecture

- **Multi-stage Build**: Optimized for production deployment
- **Frontend**: React + TypeScript + Vite (built-in)
- **Backend**: FastAPI + Python 3.12 + PostgreSQL
- **Security**: Non-root user, health checks, minimal dependencies
- **Size**: ~200MB compressed (optimized layers)

## 🔧 Health Check

The container includes built-in health checks:

```bash
## Check container health
docker ps

## Manual health check
curl http://localhost:8000/api/health
```text
## 📚 API Documentation

Once running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🚀 Production Deployment

### Docker Compose

```yaml
version: '3.8'
services:
  capecraft:
    image: stinkie/capecraft:production-ready
    ports:
      - "8000:8000"
    environment:
      - ENV=prod
      - DEBUG=false
      - DATABASE_URL=postgresql://...
      - JWT_SECRET=your-secret-key
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```text
### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: capecraft
spec:
  replicas: 3
  selector:
    matchLabels:
      app: capecraft
  template:
    metadata:
      labels:
        app: capecraft
    spec:
      containers:
      - name: capecraft
        image: stinkie/capecraft:production-ready
        ports:
        - containerPort: 8000
        env:
        - name: ENV
          value: "prod"
        - name: DEBUG
          value: "false"
        healthcheck:
          httpGet:
            path: /api/health
            port: 8000
```text
## 📖 Documentation

- **GitHub Repository**: https://github.com/robert1948/autorisen
- **Production Deployment Guide**: Available in repository docs/
- **API Documentation**: Built-in Swagger UI at `/docs`

## 🏷️ Version History

- **v1.0.0** - Initial production release with full authentication system
- **production-ready** - Optimized build with security hardening

## 📞 Support

For issues, questions, or contributions:
- **GitHub Issues**: https://github.com/robert1948/autorisen/issues
- **Live Application**: https://cape-control.com

---

Built with ❤️ for production deployment
