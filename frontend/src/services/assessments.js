import api from './api';

export const submitAssessment = async (data) => {
  const response = await api.post('/score/evaluate', data);
  return response.data;
};

// Mock endpoints for Dashboard and History as backend might not have these yet
export const getDashboardMetrics = async () => {
  // In a real scenario, this would be an API call.
  return new Promise((resolve) => setTimeout(() => resolve({
    totalAssessments: 142,
    highRisk: 12,
    avgScore: 78,
    recentTrends: [
      { month: 'Jan', score: 65 },
      { month: 'Feb', score: 68 },
      { month: 'Mar', score: 72 },
      { month: 'Apr', score: 75 },
      { month: 'May', score: 78 },
    ]
  }), 500));
};
