# Elderly Healthcare Emergency System

A comprehensive healthcare emergency management system designed for elderly patients, featuring real-time emergency alerts, hospital discovery, and contact management.

## 🚀 Features

### Backend (Django REST API)
- **User Authentication**: Token-based authentication for patients
- **Emergency Management**: Create, track, and manage emergency situations
- **Hospital Directory**: Search and manage nearby hospitals with GPS integration  
- **Emergency Contacts**: Manage personal emergency contact information
- **Notification System**: Real-time notifications to nearby hospitals
- **Dashboard Analytics**: Patient statistics and emergency metrics

### Frontend (React + Vite)
- **Modern UI**: Responsive design with Tailwind CSS
- **Real-time Dashboard**: Emergency statistics and quick actions
- **GPS Integration**: Location-based hospital discovery
- **Emergency Workflow**: One-click emergency alert system
- **Contact Management**: Easy-to-use emergency contact interface
- **Mobile-First Design**: Optimized for elderly users on all devices

## 🛠️ Tech Stack

### Backend
- **Django 5.2.6**: Python web framework
- **Django REST Framework**: API development
- **SQLite**: Database (can be upgraded to PostgreSQL)
- **Token Authentication**: Secure API access

### Frontend  
- **React 18.2.0**: Modern JavaScript library
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API calls
- **Context API**: State management

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup
1. Navigate to the project root:
   ```bash
   cd patient-management
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run database migrations:
   ```bash
   python manage.py migrate
   ```

4. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

5. Start the Django development server:
   ```bash
   python manage.py runserver
   ```
   Backend will be available at `http://localhost:8000`

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   Frontend will be available at `http://localhost:3000`

## 🔧 API Configuration

The frontend is configured to proxy API requests to the Django backend at `http://localhost:8000`. This is set up in `vite.config.js`:

```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

## 📱 Usage

### For Patients
1. **Register/Login**: Create an account or log in with existing credentials
2. **Emergency Alert**: Use the red emergency button to instantly alert nearby hospitals
3. **Manage Contacts**: Add family members and caregivers as emergency contacts  
4. **Find Hospitals**: Search for nearby hospitals with GPS-based location
5. **Track Emergencies**: Monitor the status of your emergency requests

### For Hospitals (API Integration)
- Receive real-time emergency notifications
- Access patient information during emergencies
- Update emergency status and response times
- Manage hospital information and specializations

## 🔒 Security Features

- **Token-based Authentication**: Secure API access
- **Input Validation**: Comprehensive form validation  
- **CORS Configuration**: Secure cross-origin requests
- **Error Handling**: Graceful error management
- **Data Privacy**: Patient information protection

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register/` - Patient registration
- `POST /api/auth/login/` - User login  
- `POST /api/auth/logout/` - User logout

### Emergencies
- `GET /api/emergencies/` - List patient emergencies
- `POST /api/emergencies/` - Create new emergency
- `GET /api/emergencies/{id}/` - Get emergency details
- `PATCH /api/emergencies/{id}/` - Update emergency status

### Hospitals
- `GET /api/hospitals/` - List all hospitals
- `POST /api/hospitals/` - Create new hospital
- `GET /api/hospitals/nearby/` - Find nearby hospitals
- `GET /api/hospitals/{id}/` - Get hospital details

### Emergency Contacts
- `GET /api/emergency-contacts/` - List patient contacts
- `POST /api/emergency-contacts/` - Add new contact
- `DELETE /api/emergency-contacts/{id}/` - Remove contact

### Dashboard
- `GET /api/dashboard/` - Get dashboard statistics

## 🚨 Emergency Workflow

1. **Patient clicks Emergency Alert** → System captures GPS location
2. **Create Emergency Record** → Store emergency details in database  
3. **Find Nearby Hospitals** → Query hospitals within configurable radius
4. **Send Notifications** → Alert hospitals and emergency contacts
5. **Track Response** → Monitor hospital response and patient status
6. **Status Updates** → Real-time updates on emergency resolution

## 🎨 Design Principles

- **Accessibility First**: Large buttons, high contrast, simple navigation
- **Mobile Responsive**: Touch-friendly interface for all devices
- **Emergency-Focused**: Red color scheme for urgent recognition
- **Minimal Complexity**: Streamlined UI for elderly users
- **Real-time Updates**: Live status updates and notifications

## 🔧 Development

### Running Tests
Backend tests can be run with:
```bash
python manage.py test
```

### Building for Production
Frontend production build:
```bash
npm run build
```

### Environment Variables
Configure these in Django settings:
- `DEBUG`: Set to False in production
- `ALLOWED_HOSTS`: Add your domain
- `CORS_ALLOWED_ORIGINS`: Configure frontend domains

## 🤝 Contributing

This is a hackathon project designed for demonstration purposes. Key areas for enhancement:
- Real-time WebSocket notifications
- Advanced hospital management features  
- Integration with medical devices
- Telemedicine capabilities
- Mobile app development

## 📄 License

This project is created for educational and demonstration purposes.

## 🏥 Demo Features

Perfect for hackathon demonstrations:
- **Quick Setup**: Minimal configuration required
- **Complete Workflow**: End-to-end emergency management
- **Modern UI**: Professional, responsive design
- **Real-world Simulation**: GPS integration and hospital discovery
- **Scalable Architecture**: Clean separation of concerns

---

**Emergency Hotline**: In real emergencies, always call your local emergency services (911, 112, etc.)