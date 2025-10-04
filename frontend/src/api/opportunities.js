import api from './client';

const opportunitiesAPI = {
  getOpportunities: (params = {}) => {
    const query = new URLSearchParams();
    if (params.q) query.append('q', params.q);
    if (typeof params.remote === 'boolean') query.append('remote', String(params.remote));
    if (params.limit) query.append('limit', String(params.limit));
    const suffix = query.toString() ? `?${query.toString()}` : '';
    return api.get(`/opportunities${suffix}`);
  }
};

export default opportunitiesAPI;
