# 🩸 Sheryan API (Digital Blood Donation Platform)

The robust backend service for **Sheryan**, an intelligent platform designed to bridge the gap between hospitals and blood donors. The system automates urgent relief notifications and strictly tracks safe donation intervals.

---

## 🚀 Key Features & Automated Logic
* **Smart Notification System:** Fully driven by **Django Signals (`post_save`)** to trigger immediate notifications to compatible donors as soon as a hospital creates a new blood request.
* **Data Security & Integrity:** Restricts API permissions so that donors can only read their own notifications and update the read status (`is_read`), preventing any unauthorized creation or manipulation.
* **Interactive API Documentation:** Integrated with OpenAPI 3.0 specifications to provide a live, interactive playground for the backend services.

---

## 🛠️ Tech Stack & Engineering Practices
Built and secured following industry-standard software engineering practices:
* **Framework:** Django & Django REST Framework (DRF)
* **API Design:** RESTful API Design (Clean URLs, Proper HTTP Methods & Status Codes)
* **Database & SQL:** Relational Database Design (Django ORM)
* **API Documentation:** OpenAPI 3.0 via `drf-spectacular` (Swagger & ReDoc)
* **Version Control:** Git & GitHub

> 💡 **Repository Roadmap:**
> * [ ] Containerize the entire application using **Docker & Docker Compose**.
> * [ ] Implement comprehensive automated testing using **Pytest**.
> * [ ] Build a continuous integration pipeline (**CI/CD**) via **GitHub Actions**.

---

## 📑 API Documentation
The project provides interactive documentation interfaces, allowing frontend developers (web or mobile) to easily understand and integrate with the system:

* **Swagger UI:** `http://127.0.0.1:8000/api/docs/swagger/` (To test endpoints directly from the browser).
* **ReDoc:** `http://127.0.0.1:8000/api/docs/redoc/` (A clean, highly organized layout optimized for reading).

---

## ⚙️ Local Setup Guide

1. **Clone the repository:**
```bash
   git clone [https://github.com/BAHA-d/sheryan-backend.git](https://github.com/BAHA-d/sheryan-backend.git)
   cd sheryan-backend