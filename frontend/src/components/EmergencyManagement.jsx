import React, { useState, useEffect } from 'react';
import apiService from '../services/api';

const EmergencyManagement = () => {
  const [emergencies, setEmergencies] = useState([]);
  const [selectedEmergency, setSelectedEmergency] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEmergencies();
  }, []);

  const loadEmergencies = async () => {
    try {
      const response = await apiService.getEmergencies();
      setEmergencies(response.results || response || []);
    } catch (error) {
      console.error('Failed to load emergencies:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'COMPLETED': return 'bg-green-100 text-green-800';
      case 'IN_PROGRESS': return 'bg-yellow-100 text-yellow-800';
      case 'DISPATCHED': return 'bg-blue-100 text-blue-800';
      case 'PENDING': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'CRITICAL': return 'text-red-600 bg-red-50';
      case 'HIGH': return 'text-orange-600 bg-orange-50';
      case 'MEDIUM': return 'text-yellow-600 bg-yellow-50';
      case 'LOW': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Emergency Management</h1>
        <p className="mt-2 text-gray-600">Track and manage your emergency alerts</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Emergency List */}
        <div className="lg:col-span-2">
          <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                Emergency History
              </h3>
              <p className="mt-1 max-w-2xl text-sm text-gray-500">
                All your emergency alerts and their current status
              </p>
            </div>
            <div className="border-t border-gray-200">
              {emergencies.length === 0 ? (
                <div className="text-center py-12">
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                    />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No emergencies</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    You haven't created any emergency alerts yet.
                  </p>
                </div>
              ) : (
                <ul className="divide-y divide-gray-200">
                  {emergencies.map((emergency) => (
                    <li
                      key={emergency.id}
                      className={`px-4 py-4 hover:bg-gray-50 cursor-pointer ${
                        selectedEmergency?.id === emergency.id ? 'bg-blue-50' : ''
                      }`}
                      onClick={() => setSelectedEmergency(emergency)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(emergency.priority)}`}>
                            {emergency.priority}
                          </div>
                          <div className="flex-1">
                            <p className="text-sm font-medium text-gray-900">
                              Emergency Alert #{emergency.id.substring(0, 8)}
                            </p>
                            <p className="text-sm text-gray-500">
                              {emergency.description?.substring(0, 80)}...
                            </p>
                            <div className="flex items-center mt-1 text-xs text-gray-500">
                              <svg className="mr-1 h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                              </svg>
                              {emergency.location_address || 'GPS Location'}
                            </div>
                          </div>
                        </div>
                        <div className="flex flex-col items-end">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(emergency.status)}`}>
                            {emergency.status}
                          </span>
                          <span className="text-xs text-gray-500 mt-1">
                            {new Date(emergency.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>

        {/* Emergency Details */}
        <div className="lg:col-span-1">
          {selectedEmergency ? (
            <EmergencyDetails 
              emergency={selectedEmergency} 
              onUpdate={loadEmergencies}
            />
          ) : (
            <div className="bg-white shadow sm:rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="text-center">
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">Select an Emergency</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Choose an emergency from the list to view details and updates.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Emergency Details Component
const EmergencyDetails = ({ emergency, onUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    loadNotifications();
  }, [emergency.id]);

  const loadNotifications = async () => {
    try {
      const response = await apiService.getEmergencyNotifications(emergency.id);
      setNotifications(response || []);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    }
  };

  const updateStatus = async (newStatus, notes = '') => {
    setLoading(true);
    try {
      await apiService.updateEmergencyStatus(emergency.id, {
        status: newStatus,
        response_notes: notes,
      });
      onUpdate();
    } catch (error) {
      console.error('Failed to update status:', error);
    } finally {
      setLoading(false);
    }
  };

  const completeEmergency = async () => {
    setLoading(true);
    try {
      await apiService.completeEmergency(emergency.id, {
        completion_notes: 'Emergency resolved through patient interface',
      });
      onUpdate();
    } catch (error) {
      console.error('Failed to complete emergency:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white shadow sm:rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
          Emergency Details
        </h3>
        
        <div className="space-y-4">
          <div>
            <span className="text-sm font-medium text-gray-500">Priority:</span>
            <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${
              emergency.priority === 'CRITICAL' ? 'bg-red-100 text-red-800' :
              emergency.priority === 'HIGH' ? 'bg-orange-100 text-orange-800' :
              emergency.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
              'bg-green-100 text-green-800'
            }`}>
              {emergency.priority}
            </span>
          </div>

          <div>
            <span className="text-sm font-medium text-gray-500">Status:</span>
            <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${
              emergency.status === 'COMPLETED' ? 'bg-green-100 text-green-800' :
              emergency.status === 'IN_PROGRESS' ? 'bg-yellow-100 text-yellow-800' :
              emergency.status === 'DISPATCHED' ? 'bg-blue-100 text-blue-800' :
              'bg-red-100 text-red-800'
            }`}>
              {emergency.status}
            </span>
          </div>

          <div>
            <span className="text-sm font-medium text-gray-500">Description:</span>
            <p className="mt-1 text-sm text-gray-900">{emergency.description}</p>
          </div>

          <div>
            <span className="text-sm font-medium text-gray-500">Location:</span>
            <p className="mt-1 text-sm text-gray-900">
              {emergency.location_address || `${emergency.location_latitude}, ${emergency.location_longitude}`}
            </p>
          </div>

          <div>
            <span className="text-sm font-medium text-gray-500">Created:</span>
            <p className="mt-1 text-sm text-gray-900">
              {new Date(emergency.created_at).toLocaleString()}
            </p>
          </div>

          {emergency.assigned_hospital && (
            <div>
              <span className="text-sm font-medium text-gray-500">Assigned Hospital:</span>
              <p className="mt-1 text-sm text-gray-900">{emergency.hospital_name}</p>
            </div>
          )}

          {emergency.estimated_arrival_time && (
            <div>
              <span className="text-sm font-medium text-gray-500">Estimated Arrival:</span>
              <p className="mt-1 text-sm text-gray-900">
                {new Date(emergency.estimated_arrival_time).toLocaleString()}
              </p>
            </div>
          )}

          {emergency.response_notes && (
            <div>
              <span className="text-sm font-medium text-gray-500">Response Notes:</span>
              <p className="mt-1 text-sm text-gray-900">{emergency.response_notes}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="pt-4 space-y-2">
            {emergency.status === 'PENDING' && (
              <button
                onClick={() => updateStatus('CANCELLED', 'Cancelled by patient')}
                disabled={loading}
                className="w-full px-4 py-2 text-sm font-medium text-red-700 bg-red-100 border border-red-300 rounded-md hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
              >
                Cancel Emergency
              </button>
            )}
            
            {emergency.status === 'IN_PROGRESS' && (
              <button
                onClick={completeEmergency}
                disabled={loading}
                className="w-full px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
              >
                Mark as Resolved
              </button>
            )}
          </div>

          {/* Notifications */}
          {notifications.length > 0 && (
            <div className="pt-4">
              <span className="text-sm font-medium text-gray-500">Notifications Sent:</span>
              <div className="mt-2 text-sm text-gray-600">
                {notifications.length} hospitals and contacts notified
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EmergencyManagement;