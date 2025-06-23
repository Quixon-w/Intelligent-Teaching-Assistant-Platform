import axios from 'axios'
const service = axios.create({
  baseURL: 'http://192.168.240.226:8080/',
  timeout: 10000,
  withCredentials: true,
  crossDomain: true,
  headers: {
    'Content-Type': 'application/json;charset=utf-8'
  },
})
export default service;
