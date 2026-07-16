import { secureAxios } from './secure-axios'

const api = secureAxios.getInstance()

export default api
export { api }