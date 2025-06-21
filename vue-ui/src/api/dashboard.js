import axios from 'axios'
export function onExit(){
  return Promise.reject({
    data: null,
    code: 500,
    message: 'Internal Server Error'
  })
}
