export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

export interface Feature {
  id: number;
  title: string;
  description: string;
  author_id: number;
  vote_count: number;
  created_at: string;
}

export interface Vote {
  id: number;
  user_id: number;
  feature_id: number;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface CreateUserRequest {
  username: string;
  email: string;
}

export interface CreateFeatureRequest {
  title: string;
  description: string;
}

export interface VoteResponse {
  message: string;
  vote_count: number;
}

export interface ApiError {
  detail: string;
  error_code?: string;
  timestamp?: string;
  path?: string;
  errors?: string[];
  type?: string;
}