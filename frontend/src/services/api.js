// API Service for Elderly Healthcare System
// Centralized service for all backend API interactions

const API_BASE_URL = 'http://127.0.0.1:8000/api';

class ApiService {
  constructor() {
    this.token = localStorage.getItem('authToken');
  }

  // Set authentication token
  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('authToken', token);
    } else {
      localStorage.removeItem('authToken');
    }
  }

  // Get authentication headers
  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };
    if (this.token) {
      headers['Authorization'] = `Token ${this.token}`;
    }
    return headers;
  }

  // Generic API request method
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: this.getHeaders(),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || data.detail || `HTTP ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // Authentication APIs
  async register(userData) {
    const response = await this.request('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    if (response.token) {
      this.setToken(response.token);
    }
    return response;
  }

  async login(credentials) {
    const response = await this.request('/auth/login/', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    if (response.token) {
      this.setToken(response.token);
    }
    return response;
  }

  async logout() {
    try {
      await this.request('/auth/logout/', { method: 'POST' });
    } finally {
      this.setToken(null);
    }
  }

  // User APIs
  async getUserProfile() {
    return await this.request('/users/profile/');
  }

  async updateProfile(profileData) {
    return await this.request('/users/update-profile/', {
      method: 'PATCH',
      body: JSON.stringify(profileData),
    });
  }

  async getEmergencyHistory(userId) {
    return await this.request(`/users/${userId}/emergency-history/`);
  }

  // Hospital APIs
  async getHospitals() {
    return await this.request('/hospitals/');
  }

  async createHospital(hospitalData) {
    return await this.request('/hospitals/', {
      method: 'POST',
      body: JSON.stringify(hospitalData),
    });
  }

  async getNearbyHospitals(locationData) {
    return await this.request('/hospitals/nearby/', {
      method: 'POST',
      body: JSON.stringify(locationData),
    });
  }

  async respondToEmergency(hospitalId, responseData) {
    return await this.request(`/hospitals/${hospitalId}/respond-emergency/`, {
      method: 'POST',
      body: JSON.stringify(responseData),
    });
  }

  // Emergency APIs
  async getEmergencies() {
    return await this.request('/emergencies/');
  }

  async createEmergency(emergencyData) {
    return await this.request('/emergencies/', {
      method: 'POST',
      body: JSON.stringify(emergencyData),
    });
  }

  async getEmergency(emergencyId) {
    return await this.request(`/emergencies/${emergencyId}/`);
  }

  async updateEmergencyStatus(emergencyId, statusData) {
    return await this.request(`/emergencies/${emergencyId}/update-status/`, {
      method: 'POST',
      body: JSON.stringify(statusData),
    });
  }

  async completeEmergency(emergencyId, completionData) {
    return await this.request(`/emergencies/${emergencyId}/complete/`, {
      method: 'POST',
      body: JSON.stringify(completionData),
    });
  }

  async getEmergencyNotifications(emergencyId) {
    return await this.request(`/emergencies/${emergencyId}/notifications/`);
  }

  // Emergency Contacts APIs
  async getEmergencyContacts() {
    return await this.request('/emergency-contacts/');
  }

  async createEmergencyContact(contactData) {
    return await this.request('/emergency-contacts/', {
      method: 'POST',
      body: JSON.stringify(contactData),
    });
  }

  async updateEmergencyContact(contactId, contactData) {
    return await this.request(`/emergency-contacts/${contactId}/`, {
      method: 'PUT',
      body: JSON.stringify(contactData),
    });
  }

  async deleteEmergencyContact(contactId) {
    return await this.request(`/emergency-contacts/${contactId}/`, {
      method: 'DELETE',
    });
  }

  // Ambulance APIs
  async getAmbulances() {
    return await this.request('/ambulances/');
  }

  async createAmbulance(ambulanceData) {
    return await this.request('/ambulances/', {
      method: 'POST',
      body: JSON.stringify(ambulanceData),
    });
  }

  async getAvailableAmbulances() {
    return await this.request('/ambulances/available/');
  }

  // Notifications APIs
  async getNotifications() {
    return await this.request('/notifications/');
  }

  async getUnreadNotifications() {
    return await this.request('/notifications/unread/');
  }

  async markNotificationRead(notificationId) {
    return await this.request(`/notifications/${notificationId}/mark-read/`, {
      method: 'POST',
    });
  }

  async markAllNotificationsRead() {
    return await this.request('/notifications/mark-all-read/', {
      method: 'POST',
    });
  }

  // Dashboard APIs
  async getDashboardStats() {
    return await this.request('/dashboard/');
  }

  // Utility Methods
  isAuthenticated() {
    return !!this.token;
  }

  getCurrentUserId() {
    if (!this.token) return null;
    try {
      // Basic token parsing - in production, use proper JWT decoding
      const payload = JSON.parse(atob(this.token.split('.')[1] || ''));
      return payload.user_id;
    } catch {
      return null;
    }
  }
}

// Create singleton instance
const apiService = new ApiService();
export default apiService;