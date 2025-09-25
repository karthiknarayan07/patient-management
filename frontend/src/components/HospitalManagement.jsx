import React, { useState, useEffect } from 'react';
import apiService from '../services/api';

const HospitalManagement = () => {
  const [hospitals, setHospitals] = useState([]);
  const [nearbyHospitals, setNearbyHospitals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchLoading, setSearchLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    loadHospitals();
  }, []);

  const loadHospitals = async () => {
    try {
      const response = await apiService.getHospitals();
      setHospitals(response.results || response || []);
    } catch (error) {
      console.error('Failed to load hospitals:', error);
    } finally {
      setLoading(false);
    }
  };

  const searchNearbyHospitals = async () => {
    setSearchLoading(true);
    try {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(async (position) => {
          try {
            const response = await apiService.getNearbyHospitals({
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
              radius_km: 10,
              emergency_services_only: true,
            });
            setNearbyHospitals(response.hospitals || response || []);
          } catch (error) {
            console.error('Failed to search nearby hospitals:', error);
          } finally {
            setSearchLoading(false);
          }
        }, () => {
          console.error('Location access denied');
          setSearchLoading(false);
        });
      } else {
        console.error('Geolocation not supported');
        setSearchLoading(false);
      }
    } catch (error) {
      console.error('Failed to search nearby hospitals:', error);
      setSearchLoading(false);
    }
  };

  const handleHospitalCreated = () => {
    setShowCreateModal(false);
    loadHospitals();
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
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Hospital Directory</h1>
            <p className="mt-2 text-gray-600">Find and manage healthcare facilities</p>
          </div>
          <div className="flex space-x-4">
            <button
              onClick={searchNearbyHospitals}
              disabled={searchLoading}
              className="px-4 py-2 text-sm font-medium text-blue-700 bg-blue-100 border border-blue-300 rounded-md hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {searchLoading ? 'Searching...' : 'Find Nearby'}
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              Add Hospital
            </button>
          </div>
        </div>
      </div>

      {/* Nearby Hospitals Section */}
      {nearbyHospitals.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Nearby Hospitals ({nearbyHospitals.length} found)
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {nearbyHospitals.map((hospital) => (
              <HospitalCard key={hospital.id} hospital={hospital} showDistance={true} />
            ))}
          </div>
        </div>
      )}

      {/* All Hospitals Section */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          All Hospitals ({hospitals.length})
        </h2>
        {hospitals.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
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
                d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-4m-5 0H9m0 0H5m0 0h2M7 7h10M7 11h6m-6 4h6"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No hospitals found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by adding a hospital to the directory.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {hospitals.map((hospital) => (
              <HospitalCard key={hospital.id} hospital={hospital} />
            ))}
          </div>
        )}
      </div>

      {/* Create Hospital Modal */}
      {showCreateModal && (
        <CreateHospitalModal
          onClose={() => setShowCreateModal(false)}
          onHospitalCreated={handleHospitalCreated}
        />
      )}
    </div>
  );
};

// Hospital Card Component
const HospitalCard = ({ hospital, showDistance = false }) => {
  return (
    <div className="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow duration-200">
      <div className="px-4 py-5 sm:p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900 truncate">
            {hospital.name}
          </h3>
          {hospital.operates_24x7 && (
            <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
              24/7
            </span>
          )}
        </div>

        <div className="space-y-2 text-sm text-gray-600">
          <div className="flex items-center">
            <svg className="h-4 w-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
            </svg>
            <span className="truncate">{hospital.address}</span>
          </div>

          <div className="flex items-center">
            <svg className="h-4 w-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
            </svg>
            <span>{hospital.phone_number}</span>
          </div>

          {hospital.email && (
            <div className="flex items-center">
              <svg className="h-4 w-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
              </svg>
              <span className="truncate">{hospital.email}</span>
            </div>
          )}

          {showDistance && hospital.distance_to_user && (
            <div className="flex items-center text-blue-600">
              <svg className="h-4 w-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M12 1.586l-4 4v12.828l4-4V1.586zM3.707 3.293A1 1 0 002 4v10a1 1 0 00.293.707L6 18.414V5.586L3.707 3.293zM17.707 5.293L14 1.586v12.828l2.293 2.293A1 1 0 0018 16V6a1 1 0 00-.293-.707z" clipRule="evenodd" />
              </svg>
              <span className="font-medium">{hospital.distance_to_user.toFixed(1)} km away</span>
            </div>
          )}
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {hospital.has_emergency_services && (
            <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">
              Emergency
            </span>
          )}
          {hospital.has_ambulance && (
            <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
              Ambulance ({hospital.available_ambulances}/{hospital.total_ambulances})
            </span>
          )}
        </div>

        {hospital.specializations && (
          <div className="mt-3">
            <p className="text-xs text-gray-500">
              Specializations: {hospital.specializations.substring(0, 60)}...
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

// Create Hospital Modal Component
const CreateHospitalModal = ({ onClose, onHospitalCreated }) => {
  const [formData, setFormData] = useState({
    name: '',
    registration_number: '',
    phone_number: '',
    email: '',
    website: '',
    address: '',
    city: '',
    state: '',
    pincode: '',
    latitude: '',
    longitude: '',
    has_emergency_services: true,
    has_ambulance: true,
    total_ambulances: '',
    available_ambulances: '',
    specializations: '',
    operates_24x7: true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await apiService.createHospital(formData);
      onHospitalCreated();
    } catch (error) {
      setError(error.message || 'Failed to create hospital');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData({ ...formData, [e.target.name]: value });
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center">
      <div className="relative p-8 bg-white w-full max-w-2xl m-auto rounded-lg shadow-lg max-h-screen overflow-y-auto">
        <div className="text-center mb-6">
          <h3 className="text-lg font-medium text-gray-900">Add New Hospital</h3>
          <p className="text-sm text-gray-500 mt-2">
            Register a new hospital in the emergency system
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Hospital Name *</label>
              <input
                type="text"
                name="name"
                required
                value={formData.name}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Registration Number *</label>
              <input
                type="text"
                name="registration_number"
                required
                value={formData.registration_number}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Phone Number *</label>
              <input
                type="tel"
                name="phone_number"
                required
                value={formData.phone_number}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700">Address *</label>
              <textarea
                name="address"
                required
                rows={2}
                value={formData.address}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">City *</label>
              <input
                type="text"
                name="city"
                required
                value={formData.city}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">State *</label>
              <input
                type="text"
                name="state"
                required
                value={formData.state}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Latitude</label>
              <input
                type="number"
                step="any"
                name="latitude"
                value={formData.latitude}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Longitude</label>
              <input
                type="number"
                step="any"
                name="longitude"
                value={formData.longitude}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Total Ambulances</label>
              <input
                type="number"
                name="total_ambulances"
                value={formData.total_ambulances}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Available Ambulances</label>
              <input
                type="number"
                name="available_ambulances"
                value={formData.available_ambulances}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700">Specializations</label>
              <textarea
                name="specializations"
                rows={2}
                placeholder="e.g., Emergency Medicine, Cardiology, Neurology"
                value={formData.specializations}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
              />
            </div>

            <div className="md:col-span-2 space-y-4">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="has_emergency_services"
                  checked={formData.has_emergency_services}
                  onChange={handleChange}
                  className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-900">
                  Has Emergency Services
                </label>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="has_ambulance"
                  checked={formData.has_ambulance}
                  onChange={handleChange}
                  className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-900">
                  Has Ambulance Service
                </label>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="operates_24x7"
                  checked={formData.operates_24x7}
                  onChange={handleChange}
                  className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-900">
                  Operates 24/7
                </label>
              </div>
            </div>
          </div>

          <div className="flex space-x-3 pt-6">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Hospital'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default HospitalManagement;