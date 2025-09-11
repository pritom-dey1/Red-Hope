# Blood Connector 🩸

**A Zero Boundaries Hackathon Project**  
Connects blood *donors* and *receivers* with real-time chat, map view, notifications, and more — built in Django + JS.

---

## 🔍 Problem Statement

In many places, people in urgent need of blood don’t know who nearby donors are; communication is slow; coordination and updates (availability, unread messages, donor status) are missing.  

**Blood Connector** aims to solve this by:

- Showing nearby donors on a map
- Letting receivers post blood requests
- Alerting donors of new requests via notifications  
- Enabling real-time messaging
- Showing availability & donation history  
- Managing read/unread states so nothing is missed

---

## 🎯 Key Features

| Feature | Description |
|---|---|
| **User Roles** | Donors & Receivers. Each user has a profile (blood group, picture, etc.). |
| **Donor Availability** | Donors can mark themselves available or unavailable. |
| **Map Integration** | Interactive map (Leaflet + OpenStreetMap) shows donor locations; users see donors near them. |
| **Blood Request Posts** | Receivers can post requests (blood group, location, problem). |
| **Notifications** | When a donor request is posted, relevant donors are notified. Unread notification count shown. |
| **Chat System** | AJAX-based chat between users (donors/receivers/token participants), with polling to get new messages. Unread badge for messages. |
| **Unread / Read States** | Notifications and chat messages track read/unread so you never miss anything. |
| **Contact Form** | Visitors or users can send messages via contact form (AJAX) in website. |
| **Donor-Request Approval Flow** | Receivers post requests; donors apply/donate; receiver can approve or reject. Notification sent on approval/rejection. |
| **Donation Restrictions & History** | If someone donated recently, restrict donation again before a cooldown period. Track donation history. |
| **Profile Picture Upload** | Users can upload / change profile pictures. |
| **Animations & Smooth UX** | GSAP + Locomotive Scroll for smooth scroll, hero animations, mobile menu toggles, modal windows etc. |

---

## ⚙️ Technologies Used

- **Backend**: Django (Python), with Django Auth, Models, Views, Templates  
- **Frontend**: JavaScript, HTML, CSS, GSAP animations, Locomotive Scroll, Leaflet.js for maps  
- **Database**: SQLite (development), can be switched to PostgreSQL if needed  
- **AJAX / JSON** APIs for chat messages, notifications, comment posting, etc.  
- **Email** sending (for verification, donation approval/rejection)  
- **File uploads** (profile pictures, avatars)  

---

## 📑 How It Works (Flow)

1. **Registration & Verification**  
   - User registers (username, blood group, role)  
   - Verification code emailed; activates account  

2. **Posting & Searching**  
   - Receiver posts a blood request (specifying group, location)  
   - Donors get notifications, see posts in “pluse” (feed)  

3. **Chat & Communication**  
   - Users can open chats; AJAX polling fetches new messages  
   - Unread message badges update in real time  

4. **Donor Map & Geolocation**  
   - If allowed, user's location fetched  
   - Map centers on user; nearby donor pins shown  

5. **Notification System**  
   - Requests → relevant donors get notification entries  
   - Notification modal, unread count, mark as read  

6. **Approval / Rejection Workflow**  
   - Donor applies to a request  
   - Receiver approves or rejects; email sent accordingly  

7. **Contact / Comments**  
   - Users may send messages via contact form  
   - Commenting on posts supported  

---



## 🧾 Setup & Installation

```bash
# Clone repository
git clone https://github.com/yourusername/blood-connector.git
cd blood-connector

# Set up virtual environment
python -m venv venv
source venv/bin/activate       # on Linux/Mac
# or
venv\Scripts\activate          # on Windows

# Install dependencies
pip install -r requirements.txt

# Configure settings
# - Set SECRET_KEY, DEBUG, ALLOWED_HOSTS
# - Configure email (SMTP) settings
# - (Optional) configure static/media storage

# Apply DB migrations
python manage.py migrate

# Create superuser if needed
python manage.py createsuperuser

# Run development server
python manage.py runserver

---
```
# Admin Password
- Username:pritomdey
- Password:pritom
## 👨‍💻 Developer

- Name: Pritom Dey 
- GitHub: [pritom-dey1](https://github.com/pritom-dey1)  
- LinkedIn: [Pritom Dey](https://www.linkedin.com/in/pritom-dey1/)  
- Email: pritom1.2.zx@gmail.com 

---

## 🚀 Live Demo

🔗 [Click here to view the live demo](https://zero-boundaries-hackathon.onrender.com/)  