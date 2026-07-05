import { secureAxios } from './secure-axios'

export default secureAxios.getInstance()
import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

export const adminApi = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});