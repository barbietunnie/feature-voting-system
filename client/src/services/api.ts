import axios, { type AxiosResponse } from 'axios';
import type {
  User,
  Feature,
  CreateUserRequest,
  CreateFeatureRequest,
  VoteResponse,
  PaginatedResponse,
  ApiError
} from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add user ID header
api.interceptors.request.use((config) => {
  const userId = localStorage.getItem('userId');
  if (userId && config.headers) {
    config.headers['X-User-ID'] = userId;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.data) {
      const apiError: ApiError = error.response.data;
      throw new Error(apiError.detail || 'An error occurred');
    }
    throw error;
  }
);

export const userApi = {
  // Get all users
  getUsers: async (skip = 0, limit = 100): Promise<User[]> => {
    const response: AxiosResponse<User[]> = await api.get('/users', {
      params: { skip, limit }
    });
    return response.data;
  },

  // Get user by ID
  getUser: async (id: number): Promise<User> => {
    const response: AxiosResponse<User> = await api.get(`/users/${id}`);
    return response.data;
  },

  // Create new user
  createUser: async (userData: CreateUserRequest): Promise<User> => {
    const response: AxiosResponse<User> = await api.post('/users', userData);
    return response.data;
  },
};

export const featureApi = {
  // Get paginated features
  getFeatures: async (page = 1, pageSize = 20): Promise<PaginatedResponse<Feature>> => {
    const response: AxiosResponse<PaginatedResponse<Feature>> = await api.get('/features', {
      params: { page, page_size: pageSize }
    });
    return response.data;
  },

  // Get feature by ID
  getFeature: async (id: number): Promise<Feature> => {
    const response: AxiosResponse<Feature> = await api.get(`/features/${id}`);
    return response.data;
  },

  // Create new feature
  createFeature: async (featureData: CreateFeatureRequest): Promise<Feature> => {
    const response: AxiosResponse<Feature> = await api.post('/features', featureData);
    return response.data;
  },

  // Update feature
  updateFeature: async (id: number, featureData: CreateFeatureRequest): Promise<Feature> => {
    const response: AxiosResponse<Feature> = await api.put(`/features/${id}`, featureData);
    return response.data;
  },

  // Vote for feature
  voteForFeature: async (featureId: number): Promise<VoteResponse> => {
    const response: AxiosResponse<VoteResponse> = await api.post(`/features/${featureId}/vote`);
    return response.data;
  },

  // Remove vote from feature
  removeVote: async (featureId: number): Promise<VoteResponse> => {
    const response: AxiosResponse<VoteResponse> = await api.delete(`/features/${featureId}/vote`);
    return response.data;
  },
};

export const healthApi = {
  // Health check
  healthCheck: async (): Promise<{ status: string }> => {
    const response: AxiosResponse<{ status: string }> = await api.get('/health');
    return response.data;
  },
};

export default api;