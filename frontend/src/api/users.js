import api from './client';

const usersAPI = {
  me: () => api.get('/users/me'),
  updateMe: (payload) => api.put('/users/me', payload),
};

export default usersAPI;
