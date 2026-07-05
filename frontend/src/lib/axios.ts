import { secureAxios } from './secure-axios'

// Export the secure axios instance for all API calls
export default secureAxios.getInstance()

// Export the instance directly for convenience
export const api = secureAxios.getInstance()

// Admin API uses the same secure instance
export const adminApi = secureAxios.getInstance()