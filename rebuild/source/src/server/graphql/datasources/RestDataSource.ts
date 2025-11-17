export class RestDataSource {
  protected baseURL: string;
  protected maxRetries: number;
  protected retryDelay: number;

  constructor(baseURL?: string) {
    this.baseURL = baseURL || process.env.FLASK_API_URL || 'http://localhost:8000';
    this.maxRetries = 3;
    this.retryDelay = 1000;
  }

  protected async fetch<T>(
    path: string,
    options: RequestInit = {},
    retryCount = 0
  ): Promise<T> {
    const url = `${this.baseURL}${path}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (response.status >= 500) {
        throw new Error(`Server error: ${response.status} ${response.statusText}`);
      }

      if (response.status >= 400) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Client error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data as T;
    } catch (error) {
      if (retryCount < this.maxRetries && error instanceof Error && error.message.includes('Server error')) {
        await new Promise(resolve => setTimeout(resolve, this.retryDelay * (retryCount + 1)));
        return this.fetch<T>(path, options, retryCount + 1);
      }
      
      throw error;
    }
  }

  protected async get<T>(path: string, token?: string): Promise<T> {
    return this.fetch<T>(path, {
      method: 'GET',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
  }

  protected async post<T>(path: string, body: any, token?: string): Promise<T> {
    return this.fetch<T>(path, {
      method: 'POST',
      body: JSON.stringify(body),
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
  }

  protected async put<T>(path: string, body: any, token?: string): Promise<T> {
    return this.fetch<T>(path, {
      method: 'PUT',
      body: JSON.stringify(body),
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
  }

  protected async delete<T>(path: string, token?: string): Promise<T> {
    return this.fetch<T>(path, {
      method: 'DELETE',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
  }
}
