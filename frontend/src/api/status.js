import api from './client';

const statusAPI = {
  getHealth: () => api.get('/healthz'),
  getMetrics: () => api.get('/metrics'),
};

export default statusAPI;
