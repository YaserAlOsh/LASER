import axios from "axios";

// export default axios.create({
//   withCredentials: true,
//   credentials: 'include',
  
//   headers: {
//     'Access-Control-Allow-Headers':
//       'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
//     'Access-Control-Allow-Methods': 'OPTIONS,POST',
//     'Access-Control-Allow-Credentials': true,
//     'Access-Control-Allow-Origin': '*',
//     'X-Requested-With': '*',
//     'Content-Type': "multipart/form-data"
//   }
// });
export default axios.create({
  withCredentials: true,
  credentials: 'include',
  
  headers: {
    'content-type': 'multipart/form-data',
    //'Access-Control-Allow-Headers':'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
    'Access-Control-Allow-Credentials': true,
    //'Access-Control-Allow-Origin': 'https://00cd-217-165-164-53.ngrok-free.app'
    //'X-Requested-With': '*'
  }
});





