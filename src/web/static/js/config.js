// Configuration for different environments
const Config = {
  // Detect environment based on current location
  getEnvironment() {
    const port = window.location.port;
    const hostname = window.location.hostname;
    
    // Production typically runs on port 5050
    if (port === '5050' || (port === '' && hostname !== 'localhost')) {
      return 'production';
    }
    return 'development';
  },

  // Get API base URL based on environment
  getApiBaseUrl() {
    const env = this.getEnvironment();
    const protocol = window.location.protocol;
    const hostname = window.location.hostname;
    const port = window.location.port;
    
    // For same-origin requests, use relative paths
    return '';
  },

  // API endpoints
  endpoints: {
    menuItems: '/api/menu/items',
    menuCategories: '/api/menu/categories',
    menuRecommendations: '/api/menu/recommendations',
    menuItemDetail: '/api/menu/items',
    userAction: '/api/analytics/user_action'
  },

  // Build full API URL
  buildApiUrl(endpoint, params = {}) {
    const baseUrl = this.getApiBaseUrl();
    let url = baseUrl + this.endpoints[endpoint];
    
    // Add query parameters
    const queryString = new URLSearchParams(params).toString();
    if (queryString) {
      url += '?' + queryString;
    }
    
    return url;
  },

  // Enhanced fetch with error handling and retries
  async fetchWithRetry(url, options = {}, retries = 2) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        }
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      
      console.error(`API call failed for ${url}:`, error);
      
      // Retry on network errors
      if (retries > 0 && (error.name === 'TypeError' || error.name === 'AbortError')) {
        console.log(`Retrying API call to ${url} (${retries} retries left)`);
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
        return this.fetchWithRetry(url, options, retries - 1);
      }
      
      throw error;
    }
  },

  // Debug logging
  log(message, data = null) {
    const env = this.getEnvironment();
    const timestamp = new Date().toISOString();
    
    console.log(`[${timestamp}] [${env.toUpperCase()}] ${message}`, data || '');
    
    // In production, you might want to send logs to a service
    if (env === 'production' && window.restaurantApp) {
      // Could implement remote logging here
    }
  }
};

// Log current configuration
Config.log('Configuration loaded', {
  environment: Config.getEnvironment(),
  apiBaseUrl: Config.getApiBaseUrl(),
  currentUrl: window.location.href
});

export default Config;
