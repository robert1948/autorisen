# Playbooks Overview

Source: `docs/project-plan.csv`

| ID | Title / Task | Status | Updated |
|---|---|---|---|
| AUTH-001 | Core authentication infrastructure | ✅ Completed | 2025-11-07 |
| AUTH-002 | Login/Register UI components | ✅ Completed | 2025-11-07 |
| AUTH-003 | CSRF protection implementation | ✅ Completed | 2025-11-07 |
| AUTH-004 | MFA system (TOTP) | ✅ Completed | 2025-11-07 |
| AUTH-005 | Security hardening & tests | ✅ Completed | 2025-11-07 |
| AUTH-006 | Production authentication validation | ✅ Completed | 2025-11-07 |
| FE-001 | React SPA foundation | ✅ Completed | 2025-11-07 |
| FE-002 | Routing & navigation | ✅ Completed | 2025-11-07 |
| FE-003 | Auth context & state management | ✅ Completed | 2025-11-07 |
| FE-004 | Login page + form | ✅ Completed | 2025-11-07 |
| FE-005 | Logo integration & favicon system | ✅ Completed | 2025-11-07 |
| FE-006 | Authentication flow testing | ✅ Completed | 2025-11-07 |
| UI-001 | Logo component with size variants | ✅ Completed | 2025-11-07 |
| UI-002 | Responsive logo design system | ✅ Completed | 2025-11-07 |
| DEVOPS-001 | Docker containerization | ✅ Completed | 2025-11-07 |
| DEVOPS-002 | Heroku deployment pipeline | ✅ Completed | 2025-11-07 |
| DEVOPS-003 | Environment configuration | ✅ Completed | 2025-11-07 |
| DEVOPS-004 | Database migrations | ✅ Completed | 2025-11-07 |
| DEVOPS-005 | CI/CD GitHub Actions | ✅ Completed | 2025-11-07 |
| DEVOPS-035 | Production deployment | ✅ Completed | 2025-11-07 |
| DEVOPS-036 | Static asset optimization | ✅ Completed | 2025-11-07 |
| CHAT-001 | ChatKit backend integration | 🚧 In Progress | Implement ChatKit token service and tool adapters |
| CHAT-002 | Agent registry database schema | ✅ Completed | 2025-11-08 |
| CHAT-003 | Flow orchestration API | 🕐 Todo | API endpoints for flow execution and run tracking |
| CHAT-004 | ChatKit frontend components | 🕐 Todo | CHAT-001 |
| CHAT-005 | Agent marketplace UI | 🕐 Todo | CHAT-002 |
| CHAT-006 | Developer agent builder | 🕐 Todo | CHAT-002 |
| CHAT-007 | Onboarding flow integration | 🕐 Todo | CHAT-003 |
| PAY-001 | PaymentsAgent service (PayFast) | 🚧 In Progress | PayFast adapter + ITN |
| PAY-002 | Checkout API + ChatKit tool | 🕐 Todo | PAY-001 |
| PAY-003 | ITN ingestion + audit log | 🕐 Todo | PAY-001 |
| PAY-004 | Payments DB schema | 🕐 Todo | PAY-001 |
| PAY-006 | Payments UI entry points | 🕐 Todo | PAY-002 |
| PAY-007 | Security & validation | 🕐 Todo | Server-to-server validate |
| OPT-001 | Performance monitoring | 🕐 Todo | Application monitoring and alerting setup |
| OPT-002 | Database optimization | 🕐 Todo | Query optimization and connection pooling |
| OPT-003 | Caching layer | 🕐 Todo | Redis caching for frequently accessed data |
| OPT-004 | API rate limiting | 🕐 Todo | Enhanced rate limiting for production scale |
| OPT-005 | Frontend performance audit | 🕐 Todo | Lighthouse optimization and code splitting |
| OPT-006 | Security audit | 🕐 Todo | Third-party security assessment and fixes |
| OPT-007 | Backup and disaster recovery | 🕐 Todo | Automated database backups and restore procedures |
| OPT-008 | Load testing | 🕐 Todo | Performance testing under load |
| BIZ-001 | User dashboard | 🕐 Todo | Comprehensive user dashboard with analytics |
| BIZ-002 | Admin panel | 🕐 Todo | Administrative interface for user management |
| BIZ-003 | API documentation | 🕐 Todo | Interactive API docs with examples |
| BIZ-004 | Email notifications | 🕐 Todo | Transactional email system |
| BIZ-005 | Analytics integration | 🕐 Todo | User behavior tracking and insights |
| BIZ-006 | Mobile responsiveness audit | 🕐 Todo | Comprehensive mobile UX optimization |
| BIZ-007 | Accessibility compliance | 🕐 Todo | WCAG 2.1 AA compliance implementation |
| BIZ-008 | Internationalization | 🕐 Todo | Multi-language support infrastructure |
| MAINT-001 | Dependency updates | 🔁 Recurring | Regular security and feature updates |
| MAINT-002 | Documentation maintenance | 🔁 Recurring | Keep technical documentation current |
| MAINT-003 | Test suite expansion | 🔁 Recurring | Maintain >90% test coverage |
| MAINT-004 | Performance monitoring | 🔁 Recurring | Monitor and optimize system performance |
| MAINT-005 | Security updates | 🔁 Recurring | Critical security patch management |

## ✅ Next Steps

1. Keep this index synced as playbook statuses change.
1. Ensure every new commit touching playbooks updates this table.
1. Add Phase 3 playbooks (Marketplace, Payments) once MVP stabilization is complete.
