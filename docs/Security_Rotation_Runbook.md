# Security Rotation Runbook

This runbook describes how to rotate and verify all critical secrets for the **Autorisen** project.  
Use it immediately if secrets are leaked, and at least quarterly as a preventive measure.

---

## 0. Preparation

- [ ] Enable Heroku maintenance mode:  

  ```bash
  heroku maintenance:on -a autorisen
