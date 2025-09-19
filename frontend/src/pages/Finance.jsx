import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  DollarSign, 
  Plus, 
  Edit3, 
  Trash2, 
  TrendingUp,
  TrendingDown,
  Target,
  Filter,
  Search,
  Calendar,
  PieChart,
  BarChart3,
  Wallet,
  CreditCard,
  PiggyBank
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { financeAPI } from '../api';
import { toast } from 'react-hot-toast';
import ProgressBar from '../components/ui/ProgressBar.jsx';
import Modal from '../components/ui/Modal.jsx';
import Button from '../components/ui/Button.jsx';
import Input from '../components/ui/Input.jsx';
import Textarea from '../components/ui/Textarea.jsx';
import Select from '../components/ui/Select.jsx';
import { formatCurrency } from '../utils/formatters';
import { format, subDays, startOfMonth, endOfMonth } from 'date-fns';

const Finance = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [modalType, setModalType] = useState('expense'); // 'expense', 'income', 'budget', 'goal'
  const [filters, setFilters] = useState({
    type: 'all',
    category: 'all',
    dateRange: 'month',
    search: ''
  });

  const queryClient = useQueryClient();

  // Fetch finance data
  const { data: financeData, isLoading } = useQuery({
    queryKey: ['finance-dashboard'],
    queryFn: financeAPI.getFinanceDashboard,
  });

  const { data: expenses, isLoading: expensesLoading } = useQuery({
    queryKey: ['expenses'],
    queryFn: financeAPI.getExpenses,
  });

  const { data: income, isLoading: incomeLoading } = useQuery({
    queryKey: ['income'],
    queryFn: financeAPI.getIncome,
  });

  const { data: budgets, isLoading: budgetsLoading } = useQuery({
    queryKey: ['budgets'],
    queryFn: financeAPI.getBudgets,
  });

  const { data: goals, isLoading: goalsLoading } = useQuery({
    queryKey: ['financial-goals'],
    queryFn: financeAPI.getFinancialGoals,
  });

  // Mutations
  const createExpenseMutation = useMutation({
    mutationFn: financeAPI.createExpense,
    onSuccess: () => {
      queryClient.invalidateQueries(['finance-dashboard']);
      queryClient.invalidateQueries(['expenses']);
      toast.success('Expense added successfully!');
      setIsModalOpen(false);
    },
    onError: (error) => {
      toast.error('Failed to add expense');
      console.error('Error adding expense:', error);
    },
  });

  const createIncomeMutation = useMutation({
    mutationFn: financeAPI.createIncome,
    onSuccess: () => {
      queryClient.invalidateQueries(['finance-dashboard']);
      queryClient.invalidateQueries(['income']);
      toast.success('Income added successfully!');
      setIsModalOpen(false);
    },
    onError: (error) => {
      toast.error('Failed to add income');
      console.error('Error adding income:', error);
    },
  });

  const createBudgetMutation = useMutation({
    mutationFn: financeAPI.createBudget,
    onSuccess: () => {
      queryClient.invalidateQueries(['finance-dashboard']);
      queryClient.invalidateQueries(['budgets']);
      toast.success('Budget created successfully!');
      setIsModalOpen(false);
    },
    onError: (error) => {
      toast.error('Failed to create budget');
      console.error('Error creating budget:', error);
    },
  });

  const createGoalMutation = useMutation({
    mutationFn: financeAPI.createFinancialGoal,
    onSuccess: () => {
      queryClient.invalidateQueries(['finance-dashboard']);
      queryClient.invalidateQueries(['financial-goals']);
      toast.success('Financial goal created successfully!');
      setIsModalOpen(false);
    },
    onError: (error) => {
      toast.error('Failed to create financial goal');
      console.error('Error creating financial goal:', error);
    },
  });

  const handleCreateNew = (type) => {
    setModalType(type);
    setEditingItem(null);
    setIsModalOpen(true);
  };

  const handleEdit = (item) => {
    setEditingItem(item);
    setModalType('expense');
    setIsModalOpen(true);
  };

  const handleDelete = (itemId) => {
    if (window.confirm('Are you sure you want to delete this item?')) {
      // Handle deletion based on type
      toast.success('Item deleted successfully!');
    }
  };

  const handleSubmit = (formData) => {
    if (modalType === 'expense') {
      createExpenseMutation.mutate(formData);
    } else if (modalType === 'income') {
      createIncomeMutation.mutate(formData);
    } else if (modalType === 'budget') {
      createBudgetMutation.mutate(formData);
    } else if (modalType === 'goal') {
      createGoalMutation.mutate(formData);
    }
  };

  const getDateRange = () => {
    const now = new Date();
    switch (filters.dateRange) {
      case 'week':
        return { start: subDays(now, 7), end: now };
      case 'month':
        return { start: startOfMonth(now), end: endOfMonth(now) };
      case 'quarter':
        return { start: subDays(now, 90), end: now };
      case 'year':
        return { start: subDays(now, 365), end: now };
      default:
        return { start: startOfMonth(now), end: endOfMonth(now) };
    }
  };

  if (isLoading || expensesLoading || incomeLoading || budgetsLoading || goalsLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const totalIncome = financeData?.total_income || 0;
  const totalExpenses = financeData?.total_expenses || 0;
  const netIncome = totalIncome - totalExpenses;
  const savingsRate = totalIncome > 0 ? (netIncome / totalIncome) * 100 : 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Financial Management</h1>
                <p className="mt-2 text-gray-600">
                  Track your income, expenses, and financial goals.
                </p>
              </div>
              <div className="flex space-x-3">
                <Button
                  onClick={() => handleCreateNew('expense')}
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Expense</span>
                </Button>
                <Button
                  onClick={() => handleCreateNew('income')}
                  variant="outline"
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Income</span>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Financial Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-green-50 rounded-lg">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Income</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(totalIncome)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-red-50 rounded-lg">
                <TrendingDown className="w-6 h-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Expenses</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(totalExpenses)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-blue-50 rounded-lg">
                <Wallet className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Net Income</p>
                <p className={`text-2xl font-bold ${netIncome >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(netIncome)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-purple-50 rounded-lg">
                <PiggyBank className="w-6 h-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Savings Rate</p>
                <p className="text-2xl font-bold text-gray-900">
                  {savingsRate.toFixed(1)}%
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="bg-white p-6 rounded-lg border border-gray-200 mb-8">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <Input
                  type="text"
                  placeholder="Search transactions..."
                  value={filters.search}
                  onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                  className="pl-10"
                />
              </div>
            </div>
            <Select
              value={filters.type}
              onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value }))}
              className="w-full sm:w-40"
            >
              <option value="all">All Types</option>
              <option value="expense">Expenses</option>
              <option value="income">Income</option>
            </Select>
            <Select
              value={filters.category}
              onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value }))}
              className="w-full sm:w-40"
            >
              <option value="all">All Categories</option>
              <option value="food">Food</option>
              <option value="transportation">Transportation</option>
              <option value="entertainment">Entertainment</option>
              <option value="utilities">Utilities</option>
              <option value="salary">Salary</option>
              <option value="freelance">Freelance</option>
            </Select>
            <Select
              value={filters.dateRange}
              onChange={(e) => setFilters(prev => ({ ...prev, dateRange: e.target.value }))}
              className="w-full sm:w-40"
            >
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="quarter">This Quarter</option>
              <option value="year">This Year</option>
            </Select>
          </div>
        </div>

        {/* Budgets and Goals */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Budgets Section */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Budgets</h2>
                <Button
                  onClick={() => handleCreateNew('budget')}
                  size="sm"
                  variant="outline"
                >
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
            </div>
            <div className="p-6">
              {budgets?.length === 0 ? (
                <div className="text-center py-8">
                  <Target className="mx-auto h-8 w-8 text-gray-400" />
                  <p className="mt-2 text-sm text-gray-500">No budgets set yet.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {budgets?.map((budget) => {
                    const spent = budget.spent || 0;
                    const remaining = budget.amount - spent;
                    const progress = (spent / budget.amount) * 100;
                    
                    return (
                      <div key={budget.id} className="p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-gray-900">{budget.name}</h4>
                          <span className="text-sm text-gray-500">
                            {formatCurrency(spent)} / {formatCurrency(budget.amount)}
                          </span>
                        </div>
                        <ProgressBar 
                          progress={progress} 
                          size="sm"
                          color={progress > 80 ? 'red' : progress > 60 ? 'yellow' : 'green'}
                        />
                        <div className="flex justify-between text-sm text-gray-600 mt-2">
                          <span>Remaining: {formatCurrency(remaining)}</span>
                          <span>{progress.toFixed(1)}% used</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Financial Goals Section */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Financial Goals</h2>
                <Button
                  onClick={() => handleCreateNew('goal')}
                  size="sm"
                  variant="outline"
                >
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
            </div>
            <div className="p-6">
              {goals?.length === 0 ? (
                <div className="text-center py-8">
                  <Target className="mx-auto h-8 w-8 text-gray-400" />
                  <p className="mt-2 text-sm text-gray-500">No financial goals set yet.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {goals?.map((goal) => {
                    const progress = (goal.current_amount / goal.target_amount) * 100;
                    
                    return (
                      <div key={goal.id} className="p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-gray-900">{goal.title}</h4>
                          <span className="text-sm text-gray-500">
                            {formatCurrency(goal.current_amount)} / {formatCurrency(goal.target_amount)}
                          </span>
                        </div>
                        <ProgressBar 
                          progress={progress} 
                          size="sm"
                        />
                        <div className="flex justify-between text-sm text-gray-600 mt-2">
                          <span>Remaining: {formatCurrency(goal.target_amount - goal.current_amount)}</span>
                          <span>{progress.toFixed(1)}% complete</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="bg-white rounded-lg border border-gray-200 mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Recent Transactions</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {expenses?.slice(0, 5).map((expense) => (
                <div key={expense.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="p-2 bg-red-100 rounded-lg">
                      <TrendingDown className="w-5 h-5 text-red-600" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">{expense.description}</h4>
                      <p className="text-sm text-gray-500">{expense.category}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-red-600">-{formatCurrency(expense.amount)}</p>
                    <p className="text-sm text-gray-500">
                      {format(new Date(expense.date), 'MMM d, yyyy')}
                    </p>
                  </div>
                </div>
              ))}
              {income?.slice(0, 3).map((incomeItem) => (
                <div key={incomeItem.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <TrendingUp className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">{incomeItem.description}</h4>
                      <p className="text-sm text-gray-500">{incomeItem.category}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-green-600">+{formatCurrency(incomeItem.amount)}</p>
                    <p className="text-sm text-gray-500">
                      {format(new Date(incomeItem.date), 'MMM d, yyyy')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button 
                onClick={() => handleCreateNew('expense')}
                className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-400 hover:bg-primary-50 transition-colors text-center"
              >
                <Plus className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="font-medium text-gray-700">Add Expense</p>
              </button>
              <button 
                onClick={() => handleCreateNew('income')}
                className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-400 hover:bg-primary-50 transition-colors text-center"
              >
                <TrendingUp className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="font-medium text-gray-700">Add Income</p>
              </button>
              <button 
                onClick={() => handleCreateNew('goal')}
                className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-400 hover:bg-primary-50 transition-colors text-center"
              >
                <Target className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="font-medium text-gray-700">Set Goal</p>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingItem(null);
        }}
        title={
          modalType === 'expense' ? 'Add Expense' :
          modalType === 'income' ? 'Add Income' :
          modalType === 'budget' ? 'Create Budget' :
          'Create Financial Goal'
        }
      >
        <FinanceForm
          type={modalType}
          editingItem={editingItem}
          onSubmit={handleSubmit}
          onCancel={() => {
            setIsModalOpen(false);
            setEditingItem(null);
          }}
        />
      </Modal>
    </div>
  );
};

// Form Component
const FinanceForm = ({ type, editingItem, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    amount: editingItem?.amount || '',
    description: editingItem?.description || '',
    category: editingItem?.category || '',
    date: editingItem?.date ? editingItem.date.split('T')[0] : new Date().toISOString().split('T')[0],
    notes: editingItem?.notes || '',
    name: editingItem?.name || '', // for budgets and goals
    target_amount: editingItem?.target_amount || '', // for goals
    current_amount: editingItem?.current_amount || '', // for goals
    target_date: editingItem?.target_date ? editingItem.target_date.split('T')[0] : '', // for goals
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  if (type === 'budget') {
    return (
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Budget Name
          </label>
          <Input
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="e.g., Groceries, Entertainment"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Amount
          </label>
          <Input
            type="number"
            name="amount"
            value={formData.amount}
            onChange={handleChange}
            placeholder="0.00"
            step="0.01"
            min="0"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Category
          </label>
          <Select
            name="category"
            value={formData.category}
            onChange={handleChange}
            required
          >
            <option value="">Select category</option>
            <option value="food">Food</option>
            <option value="transportation">Transportation</option>
            <option value="entertainment">Entertainment</option>
            <option value="utilities">Utilities</option>
            <option value="shopping">Shopping</option>
            <option value="health">Health</option>
          </Select>
        </div>
        <div className="flex justify-end space-x-3 pt-4">
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit">
            Create Budget
          </Button>
        </div>
      </form>
    );
  }

  if (type === 'goal') {
    return (
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Goal Title
          </label>
          <Input
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="e.g., Emergency Fund, Vacation"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Target Amount
          </label>
          <Input
            type="number"
            name="target_amount"
            value={formData.target_amount}
            onChange={handleChange}
            placeholder="0.00"
            step="0.01"
            min="0"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Current Amount
          </label>
          <Input
            type="number"
            name="current_amount"
            value={formData.current_amount}
            onChange={handleChange}
            placeholder="0.00"
            step="0.01"
            min="0"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Target Date
          </label>
          <Input
            type="date"
            name="target_date"
            value={formData.target_date}
            onChange={handleChange}
          />
        </div>
        <div className="flex justify-end space-x-3 pt-4">
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit">
            Create Goal
          </Button>
        </div>
      </form>
    );
  }

  // Default expense/income form
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Amount
        </label>
        <Input
          type="number"
          name="amount"
          value={formData.amount}
          onChange={handleChange}
          placeholder="0.00"
          step="0.01"
          min="0"
          required
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <Input
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder={type === 'expense' ? 'e.g., Grocery shopping' : 'e.g., Salary payment'}
          required
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Category
        </label>
        <Select
          name="category"
          value={formData.category}
          onChange={handleChange}
          required
        >
          <option value="">Select category</option>
          {type === 'expense' ? (
            <>
              <option value="food">Food</option>
              <option value="transportation">Transportation</option>
              <option value="entertainment">Entertainment</option>
              <option value="utilities">Utilities</option>
              <option value="shopping">Shopping</option>
              <option value="health">Health</option>
              <option value="education">Education</option>
            </>
          ) : (
            <>
              <option value="salary">Salary</option>
              <option value="freelance">Freelance</option>
              <option value="investment">Investment</option>
              <option value="gift">Gift</option>
              <option value="other">Other</option>
            </>
          )}
        </Select>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Date
        </label>
        <Input
          type="date"
          name="date"
          value={formData.date}
          onChange={handleChange}
          required
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Notes
        </label>
        <Textarea
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          placeholder="Additional notes..."
          rows={3}
        />
      </div>
      <div className="flex justify-end space-x-3 pt-4">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit">
          {type === 'expense' ? 'Add Expense' : 'Add Income'}
        </Button>
      </div>
    </form>
  );
};

export default Finance;
