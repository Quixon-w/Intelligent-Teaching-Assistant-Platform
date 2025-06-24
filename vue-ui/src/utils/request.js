import axios from 'axios'
const service = axios.create({
  //baseURL: 'http://localhost:8080/api/',
  timeout: q10000,
  withCredentials: true,
})
export default service;
