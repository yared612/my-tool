import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'https://mytool-6736aca6ec4e.herokuapp.com',
  withCredentials: true,
});

export default axiosInstance;
