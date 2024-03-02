import axios from "axios";

export default axios.create({
  withCredentials: true,
  credentials: 'include',
  crossdomain: true,
  headers: {
    'Content-Type': 'application/json',
    //'Access-Control-Allow-Headers':'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
    //'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
    //'Access-Control-Allow-Credentials': true,
    //'Access-Control-Allow-Origin': 'https://00cd-217-165-164-53.ngrok-free.app'
    //'X-Requested-With': '*'

  }
});


