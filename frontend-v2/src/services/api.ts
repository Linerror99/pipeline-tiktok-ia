// API Service pour communiquer avec le backend
import { API_CONFIG, ACCESS_CODE } from '../config/api';

const API_BASE_URL = API_CONFIG.baseURL;
const WS_BASE_URL = API_CONFIG.wsURL;

export interface VideoCreateRequest {
  theme: string;
  access_code: string;
  target_duration?: number;
  style?: string;
  language?: string;
}

export interface VideoResponse {
  video_id: string;
  status: string;
  message: string;
  theme: string;
  blocks_generated?: number;
  duration?: number;
}

export interface VideoStatus {
  video_id: string;
  status: string;
  current_step?: string;
  total_blocks?: number;
  completed_blocks?: number;
  progress?: number;
  error_message?: string;
  final_url?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Video {
  id: string;
  theme: string;
  status: string;
  created_at: string;
  video_url?: string;
  thumbnail_url?: string;
  duration?: number;
  blocks_count?: number;
}

class ApiService {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('auth_token');
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      this.clearToken();
      throw new Error('Unauthorized');
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Auth
  async login(email: string, password: string) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  async register(email: string, password: string) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async getCurrentUser() {
    return this.request('/auth/me', { method: 'GET' });
  }

  // Videos
  async createVideo(params: Omit<VideoCreateRequest, 'access_code'>): Promise<VideoResponse> {
    return this.request('/videos/create', {
      method: 'POST',
      body: JSON.stringify({
        ...params,
        access_code: ACCESS_CODE, // Use configured access code
      }),
    });
  }

  async listVideos(): Promise<{ videos: Video[]; count: number }> {
    return this.request('/videos', { method: 'GET' });
  }

  async getVideoStatus(videoId: string): Promise<VideoStatus> {
    return this.request(`/videos/${videoId}/status`, { method: 'GET' });
  }

  async getVideo(videoId: string): Promise<Video> {
    return this.request(`/videos/${videoId}`, { method: 'GET' });
  }

  async getVideoUrl(videoId: string): Promise<string> {
    const response = await this.request<{ download_url: string }>(
      `/videos/${videoId}/download`,
      { method: 'GET' }
    );
    return response.download_url;
  }

  async getVideoStreamUrl(videoId: string): Promise<string> {
    const response = await this.request<{ stream_url: string }>(
      `/videos/${videoId}/stream`,
      { method: 'GET' }
    );
    return response.stream_url;
  }

  async deleteVideo(videoId: string): Promise<void> {
    return this.request(`/videos/${videoId}`, { method: 'DELETE' });
  }

  // WebSocket
  createWebSocket(videoId: string): WebSocket {
    const token = this.getToken();
    return new WebSocket(`${WS_BASE_URL}/ws/video/${videoId}?token=${token}`);
  }
}

export const apiService = new ApiService();
