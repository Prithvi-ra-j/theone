"""Finance models for expense tracking and budget management."""

from datetime import datetime, date
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Date, ForeignKey, Integer, String, Text, Float, Numeric
from sqlalchemy.orm import relationship

from ..db.session import Base


class Expense(Base):
    """Expense tracking model."""
    
    __tablename__ = "expense"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)  # Using Numeric for precise decimal handling
    description = Column(String(500), nullable=False)
    category = Column(String(100), nullable=False)  # e.g., 'food', 'transport', 'education', 'entertainment'
    subcategory = Column(String(100), nullable=True)  # e.g., 'restaurant', 'groceries' under 'food'
    
    # Transaction details
    date = Column(Date, default=date.today, nullable=False)
    payment_method = Column(String(50), nullable=True)  # 'cash', 'card', 'upi', 'bank_transfer'
    merchant = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    
    # Recurring expenses
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurring_frequency = Column(String(20), nullable=True)  # 'weekly', 'monthly', 'yearly'
    
    # Additional info
    notes = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    receipt_url = Column(String(500), nullable=True)  # URL to receipt image/file
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="expenses")
    
    def __repr__(self) -> str:
        return f"<Expense(id={self.id}, amount={self.amount}, category='{self.category}')>"


class Budget(Base):
    """Budget planning and tracking model."""
    
    __tablename__ = "budget"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # matches expense categories
    amount = Column(Numeric(10, 2), nullable=False)  # budget limit
    
    # Budget period
    period_type = Column(String(20), default="monthly", nullable=False)  # 'weekly', 'monthly', 'yearly', 'custom'
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)  # null for ongoing budgets
    
    # Tracking
    spent_amount = Column(Numeric(10, 2), default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    alert_threshold = Column(Float, default=80.0, nullable=False)  # percentage (80% = alert at 80% of budget)
    alert_enabled = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="budgets")
    
    @property
    def remaining_amount(self) -> float:
        """Calculate remaining budget amount."""
        return float(self.amount - self.spent_amount)
    
    @property
    def spent_percentage(self) -> float:
        """Calculate percentage of budget spent."""
        if self.amount == 0:
            return 0.0
        return float((self.spent_amount / self.amount) * 100)
    
    def __repr__(self) -> str:
        return f"<Budget(id={self.id}, name='{self.name}', amount={self.amount})>"


class Income(Base):
    """Income tracking model."""
    
    __tablename__ = "income"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    source = Column(String(255), nullable=False)  # e.g., 'salary', 'freelance', 'scholarship', 'part_time'
    description = Column(String(500), nullable=True)
    
    # Income details
    date_received = Column(Date, default=date.today, nullable=False)
    payment_method = Column(String(50), nullable=True)
    
    # Recurring income
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurring_frequency = Column(String(20), nullable=True)  # 'weekly', 'monthly', 'yearly'
    
    # Tax information
    is_taxable = Column(Boolean, default=True, nullable=False)
    tax_amount = Column(Numeric(10, 2), nullable=True)
    
    # Additional info
    notes = Column(Text, nullable=True)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="incomes")
    
    def __repr__(self) -> str:
        return f"<Income(id={self.id}, amount={self.amount}, source='{self.source}')>"


class FinancialGoal(Base):
    """Financial goal setting and tracking model."""
    
    __tablename__ = "financialgoal"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    goal_type = Column(String(50), nullable=False)  # 'savings', 'investment', 'debt_payoff', 'purchase'
    
    # Goal amounts
    target_amount = Column(Numeric(10, 2), nullable=False)
    current_amount = Column(Numeric(10, 2), default=0, nullable=False)
    
    # Timeline
    target_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Status
    status = Column(String(20), default="active", nullable=False)  # 'active', 'completed', 'paused', 'cancelled'
    priority = Column(String(20), default="medium", nullable=False)  # 'low', 'medium', 'high'
    
    # Progress tracking
    monthly_contribution = Column(Numeric(10, 2), nullable=True)  # planned monthly contribution
    
    # Relationships
    user = relationship("User", back_populates="financial_goals")
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage towards goal."""
        if self.target_amount == 0:
            return 0.0
        return float((self.current_amount / self.target_amount) * 100)
    
    @property
    def remaining_amount(self) -> float:
        """Calculate remaining amount to reach goal."""
        return float(self.target_amount - self.current_amount)
    
    def __repr__(self) -> str:
        return f"<FinancialGoal(id={self.id}, title='{self.title}', target={self.target_amount})>"