import { request } from 'axios'
export function login(username, password) {
  return request({
    method: 'post',
    url: 'http://localhost:8080/',
    data: {
      username,
      password,
    }
  }).then(response => {
    console.log(response);
    return true;
  }).catch(error => {
    console.log(error);
    return false;
  });
}
