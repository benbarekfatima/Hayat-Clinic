# 🏥 Hayat Clinic

A web application for managing medical appointments, patient records, and clinic operations — built with Django.

---

## 🚀 Features

- Patient registration and login  
- Book, edit, or cancel appointments  
- Doctor profiles and schedules  
- Admin dashboard for managing users, appointments, and records  
- Email notifications for appointments  
- Secure authentication system  

---

## 🛠️ Technologies

- Python & Django  
- SQLite (default DB)  
- HTML/CSS with Bootstrap  
- JavaScript (for interactivity)  
- Django Templates  

---

## Project Structure 

```bash
Hayat-Clinic/
├── manage.py
├── db.sqlite3
├── Project/                # Main Django app
├── SIProject/              # Django settings and URLs
└── templates/              # HTML templates
```

## 📦 Installation

```bash
git clone https://github.com/benbarekfatima/Hayat-Clinic.git
cd Hayat-Clinic
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -requirements- (install django : pip install django )
python manage.py migrate
python manage.py runserver
```

## Improvements
 - Add search/filter for doctors
 - Connect to a real email provider
 - Deploy to Render or Railway
 - Add unit tests
