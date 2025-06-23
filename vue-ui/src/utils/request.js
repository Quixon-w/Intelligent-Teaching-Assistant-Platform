import axios from 'axios'
const service = axios.create({
  baseURL: 'http://192.168.240.226:8080/',
  timeout: 10000,
  withCredentials: true,
})
export default service;
