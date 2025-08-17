# ✅ CapeControl Sanity Test Plan

_Last updated: 2025-06-16_

This test plan ensures the frontend, backend, and database are correctly wired and functional after containerized deployment.

---

## 🌐 1. Web Access Test

### ✅ Home Page
- [ ] Open [http://localhost:8000](http://localhost:8000)
- [ ] Confirm the React frontend loads successfully

### ✅ Static File Routing
- [ ] Navigate to [http://localhost:8000/login](http://localhost:8000/login)
- [ ] Confirm that client-side routing works via React

---

## 🔁 2. Backend API Test

### ✅ Health Check
- [ ] Open [http://localhost:8000/](http://localhost:8000/)
- [ ] Confirm JSON:  
  ```json
  { "message": "CapeControl API running." }
  ```

### ✅ Auth Routes
Using Postman, Insomnia, or `curl`:

#### ➕ Register
```http
POST http://localhost:8000/register
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "password123"
}
```
- [ ] Returns 200 OK and user JSON

#### 🔐 Login
```http
POST http://localhost:8000/login
Content-Type: application/x-www-form-urlencoded

grant_type=&username=test@example.com&password=password123&scope=&client_id=&client_secret=
```
- [ ] Returns 200 OK with access token

#### 👤 /me
```http
GET http://localhost:8000/me
Authorization: Bearer <access_token>
```
- [ ] Returns authenticated user info

---

## 🛢️ 3. Database Connectivity

- [ ] Confirm tables were auto-created
- [ ] `capecntl-db` logs show successful connections
- [ ] No connection timeout or auth errors

---

## 🧪 4. Optional Swagger UI Test
- [ ] Visit [http://localhost:8000/docs](http://localhost:8000/docs)
- [ ] Test `/register`, `/login`, and `/me` interactively

---

## ✅ Success Criteria
- No 500 errors in logs
- All endpoints return expected results
- Database persists users correctly
- Static frontend and React routes load without reload failure
