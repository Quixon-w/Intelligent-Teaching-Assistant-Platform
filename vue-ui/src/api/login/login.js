import axios from 'axios'
export function login(username, password) {
  return axios.request({
    method: 'post',
    url: 'http://192.168.240.226:8080/user/login',
    data: {
      "userAccount": username,
      "userPassword": password,
    }
  }).then(response => {
    return response;
  }).catch(error => {
    return error;
  });
}
