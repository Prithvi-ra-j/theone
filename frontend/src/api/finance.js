/**
 * Finance API Module
 * Handles all finance-related API calls including expenses, income, budgets, and financial goals
 */

import api from './client';

const FINANCE_BASE_URL = '/finance';

const financeAPI = {
  // Expenses
  getExpenses: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.category) queryParams.append('category', params.category);
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.amount_min) queryParams.append('amount_min', params.amount_min);
    if (params.amount_max) queryParams.append('amount_max', params.amount_max);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${FINANCE_BASE_URL}/expenses?${queryParams.toString()}`
      : `${FINANCE_BASE_URL}/expenses`;
    
    return api.get(url);
  },

  getExpense: (expenseId) => 
    api.get(`${FINANCE_BASE_URL}/expenses/${expenseId}`),

  createExpense: (expenseData) => 
    api.post(`${FINANCE_BASE_URL}/expenses`, expenseData),

  updateExpense: (expenseId, expenseData) => 
    api.put(`${FINANCE_BASE_URL}/expenses/${expenseId}`, expenseData),

  deleteExpense: (expenseId) => 
    api.delete(`${FINANCE_BASE_URL}/expenses/${expenseId}`),

  // Income
  getIncome: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.source) queryParams.append('source', params.source);
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.amount_min) queryParams.append('amount_min', params.amount_min);
    if (params.amount_max) queryParams.append('amount_max', params.amount_max);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${FINANCE_BASE_URL}/income?${queryParams.toString()}`
      : `${FINANCE_BASE_URL}/income`;
    
    return api.get(url);
  },

  getIncomeEntry: (incomeId) => 
    api.get(`${FINANCE_BASE_URL}/income/${incomeId}`),

  createIncome: (incomeData) => 
    api.post(`${FINANCE_BASE_URL}/income`, incomeData),

  updateIncome: (incomeId, incomeData) => 
    api.put(`${FINANCE_BASE_URL}/income/${incomeId}`, incomeData),

  deleteIncome: (incomeId) => 
    api.delete(`${FINANCE_BASE_URL}/income/${incomeId}`),

  // Budgets
  getBudgets: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.category) queryParams.append('category', params.category);
    if (params.status) queryParams.append('status', params.status);
    if (params.period) queryParams.append('period', params.period);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${FINANCE_BASE_URL}/budgets?${queryParams.toString()}`
      : `${FINANCE_BASE_URL}/budgets`;
    
    return api.get(url);
  },

  getBudget: (budgetId) => 
    api.get(`${FINANCE_BASE_URL}/budgets/${budgetId}`),

  createBudget: (budgetData) => 
    api.post(`${FINANCE_BASE_URL}/budgets`, budgetData),

  updateBudget: (budgetId, budgetData) => 
    api.put(`${FINANCE_BASE_URL}/budgets/${budgetId}`, budgetData),

  deleteBudget: (budgetId) => 
    api.delete(`${FINANCE_BASE_URL}/budgets/${budgetId}`),

  updateBudgetAmount: (budgetId, amount) => 
    api.patch(`${FINANCE_BASE_URL}/budgets/${budgetId}/amount`, { amount }),

  // Financial Goals
  getFinancialGoals: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.status) queryParams.append('status', params.status);
    if (params.priority) queryParams.append('priority', params.priority);
    if (params.category) queryParams.append('category', params.category);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${FINANCE_BASE_URL}/goals?${queryParams.toString()}`
      : `${FINANCE_BASE_URL}/goals`;
    
    return api.get(url);
  },

  getFinancialGoal: (goalId) => 
    api.get(`${FINANCE_BASE_URL}/goals/${goalId}`),

  createFinancialGoal: (goalData) => 
    api.post(`${FINANCE_BASE_URL}/goals`, goalData),

  updateFinancialGoal: (goalId, goalData) => 
    api.put(`${FINANCE_BASE_URL}/goals/${goalId}`, goalData),

  deleteFinancialGoal: (goalId) => 
    api.delete(`${FINANCE_BASE_URL}/goals/${goalId}`),

  updateGoalProgress: (goalId, progress) => 
    api.patch(`${FINANCE_BASE_URL}/goals/${goalId}/progress`, { progress }),

  // Finance Dashboard
  getFinanceDashboard: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.date) queryParams.append('date', params.date);
    if (params.period) queryParams.append('period', params.period);
    
    const url = queryParams.toString() 
      ? `${FINANCE_BASE_URL}/dashboard?${queryParams.toString()}`
      : `${FINANCE_BASE_URL}/dashboard`;
    
    return api.get(url);
  },

  // Financial Analytics
  getExpenseAnalytics: (timeframe = 'month', params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.category) queryParams.append('category', params.category);
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    
    const url = queryParams.toString() 
      ? `${FINANCE_BASE_URL}/analytics/expenses?timeframe=${timeframe}&${queryParams.toString()}`
      : `${FINANCE_BASE_URL}/analytics/expenses?timeframe=${timeframe}`;
    
    return api.get(url);
  },

  getIncomeAnalytics: (timeframe = 'month', params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.source) queryParams.append('source', params.source);
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    
    const url = queryParams.toString() 
      ? `${FINANCE_BASE_URL}/analytics/income?timeframe=${timeframe}&${queryParams.toString()}`
      : `${FINANCE_BASE_URL}/analytics/income?timeframe=${timeframe}`;
    
    return api.get(url);
  },

  getBudgetAnalytics: (timeframe = 'month') => 
    api.get(`${FINANCE_BASE_URL}/analytics/budgets?timeframe=${timeframe}`),

  getSavingsAnalytics: (timeframe = 'month') => 
    api.get(`${FINANCE_BASE_URL}/analytics/savings?timeframe=${timeframe}`),

  getNetWorthHistory: (timeframe = 'year') => 
    api.get(`${FINANCE_BASE_URL}/analytics/net-worth?timeframe=${timeframe}`),

  // Categories
  getExpenseCategories: () => 
    api.get(`${FINANCE_BASE_URL}/categories/expenses`),

  getIncomeCategories: () => 
    api.get(`${FINANCE_BASE_URL}/categories/income`),

  createExpenseCategory: (categoryData) => 
    api.post(`${FINANCE_BASE_URL}/categories/expenses`, categoryData),

  createIncomeCategory: (categoryData) => 
    api.post(`${FINANCE_BASE_URL}/categories/income`, categoryData),

  updateExpenseCategory: (categoryId, categoryData) => 
    api.put(`${FINANCE_BASE_URL}/categories/expenses/${categoryId}`, categoryData),

  updateIncomeCategory: (categoryId, categoryData) => 
    api.put(`${FINANCE_BASE_URL}/categories/income/${categoryId}`, categoryData),

  deleteExpenseCategory: (categoryId) => 
    api.delete(`${FINANCE_BASE_URL}/categories/expenses/${categoryId}`),

  deleteIncomeCategory: (categoryId) => 
    api.delete(`${FINANCE_BASE_URL}/categories/income/${categoryId}`),

  // Recurring Transactions
  getRecurringExpenses: () => 
    api.get(`${FINANCE_BASE_URL}/recurring/expenses`),

  getRecurringIncome: () => 
    api.get(`${FINANCE_BASE_URL}/recurring/income`),

  createRecurringExpense: (expenseData) => 
    api.post(`${FINANCE_BASE_URL}/recurring/expenses`, expenseData),

  createRecurringIncome: (incomeData) => 
    api.post(`${FINANCE_BASE_URL}/recurring/income`, incomeData),

  updateRecurringExpense: (expenseId, expenseData) => 
    api.put(`${FINANCE_BASE_URL}/recurring/expenses/${expenseId}`, expenseData),

  updateRecurringIncome: (incomeId, incomeData) => 
    api.put(`${FINANCE_BASE_URL}/recurring/income/${incomeId}`, incomeData),

  deleteRecurringExpense: (expenseId) => 
    api.delete(`${FINANCE_BASE_URL}/recurring/expenses/${expenseId}`),

  deleteRecurringIncome: (incomeId) => 
    api.delete(`${FINANCE_BASE_URL}/recurring/income/${incomeId}`),

  // Financial Planning
  getFinancialPlan: () => 
    api.get(`${FINANCE_BASE_URL}/plan`),

  createFinancialPlan: (planData) => 
    api.post(`${FINANCE_BASE_URL}/plan`, planData),

  updateFinancialPlan: (planId, planData) => 
    api.put(`${FINANCE_BASE_URL}/plan/${planId}`, planData),

  deleteFinancialPlan: (planId) => 
    api.delete(`${FINANCE_BASE_URL}/plan/${planId}`),

  // Investment Tracking
  getInvestments: () => 
    api.get(`${FINANCE_BASE_URL}/investments`),

  getInvestment: (investmentId) => 
    api.get(`${FINANCE_BASE_URL}/investments/${investmentId}`),

  createInvestment: (investmentData) => 
    api.post(`${FINANCE_BASE_URL}/investments`, investmentData),

  updateInvestment: (investmentId, investmentData) => 
    api.put(`${FINANCE_BASE_URL}/investments/${investmentId}`, investmentData),

  deleteInvestment: (investmentId) => 
    api.delete(`${FINANCE_BASE_URL}/investments/${investmentId}`),

  // Debt Tracking
  getDebts: () => 
    api.get(`${FINANCE_BASE_URL}/debts`),

  getDebt: (debtId) => 
    api.get(`${FINANCE_BASE_URL}/debts/${debtId}`),

  createDebt: (debtData) => 
    api.post(`${FINANCE_BASE_URL}/debts`, debtData),

  updateDebt: (debtId, debtData) => 
    api.put(`${FINANCE_BASE_URL}/debts/${debtId}`, debtData),

  deleteDebt: (debtId) => 
    api.delete(`${FINANCE_BASE_URL}/debts/${debtId}`),

  // Financial Reports
  generateExpenseReport: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.category) queryParams.append('category', params.category);
    if (params.format) queryParams.append('format', params.format);
    
    const url = queryParams.toString() 
      ? `${FINANCE_BASE_URL}/reports/expenses?${queryParams.toString()}`
      : `${FINANCE_BASE_URL}/reports/expenses`;
    
    return api.download(url);
  },

  generateIncomeReport: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.source) queryParams.append('source', params.source);
    if (params.format) queryParams.append('format', params.format);
    
    const url = queryParams.toString() 
      ? `${FINANCE_BASE_URL}/reports/income?${queryParams.toString()}`
      : `${FINANCE_BASE_URL}/reports/income`;
    
    return api.download(url);
  },

  generateBudgetReport: (period = 'month') => 
    api.download(`${FINANCE_BASE_URL}/reports/budgets?period=${period}`),

  // AI Financial Advice
  getFinancialAdvice: (query, context = {}) => 
    api.post(`${FINANCE_BASE_URL}/advice`, { query, context }),

  getBudgetRecommendations: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.income) queryParams.append('income', params.income);
    if (params.expenses) queryParams.append('expenses', params.expenses);
    if (params.goals) queryParams.append('goals', params.goals);
    
    const url = queryParams.toString() 
      ? `${FINANCE_BASE_URL}/recommendations/budget?${queryParams.toString()}`
      : `${FINANCE_BASE_URL}/recommendations/budget`;
    
    return api.get(url);
  },

  // Export/Import
  exportFinanceData: (format = 'json') => 
    api.download(`${FINANCE_BASE_URL}/export?format=${format}`),

  importFinanceData: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.upload(`${FINANCE_BASE_URL}/import`, formData);
  },

  // Bulk Operations
  bulkUpdateExpenses: (expenseIds, updateData) => 
    api.patch(`${FINANCE_BASE_URL}/expenses/bulk-update`, { expense_ids: expenseIds, ...updateData }),

  bulkDeleteExpenses: (expenseIds) => 
    api.delete(`${FINANCE_BASE_URL}/expenses/bulk-delete`, { data: { expense_ids: expenseIds } }),

  bulkCategorizeExpenses: (expenseIds, categoryId) => 
    api.patch(`${FINANCE_BASE_URL}/expenses/bulk-categorize`, { expense_ids: expenseIds, category_id: categoryId }),
};

export default financeAPI;
