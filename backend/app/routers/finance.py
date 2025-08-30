"""Finance router for managing expenses, budgets, and financial goals."""

from typing import Any, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.user import User
from app.models.finance import Expense, Budget, Income, FinancialGoal
from app.routers.auth import get_current_user

router = APIRouter()


# Expenses
@router.post("/expenses", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_expense(
    amount: float,
    description: str,
    category: str,
    subcategory: str = None,
    payment_method: str = None,
    is_recurring: bool = False,
    recurring_frequency: str = None,
    notes: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new expense."""
    db_expense = Expense(
        user_id=current_user.id,
        amount=amount,
        description=description,
        category=category,
        subcategory=subcategory,
        payment_method=payment_method,
        is_recurring=is_recurring,
        recurring_frequency=recurring_frequency,
        notes=notes
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return {"message": "Expense created successfully", "expense_id": db_expense.id}


@router.get("/expenses", response_model=List[dict])
async def get_expenses(
    category: str = None,
    start_date: str = None,
    end_date: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all expenses for the current user."""
    query = db.query(Expense).filter(Expense.user_id == current_user.id)
    
    if category:
        query = query.filter(Expense.category == category)
    
    if start_date:
        query = query.filter(Expense.date >= start_date)
    
    if end_date:
        query = query.filter(Expense.date <= end_date)
    
    expenses = query.order_by(Expense.date.desc()).all()
    
    return [
        {
            "id": expense.id,
            "amount": float(expense.amount),
            "description": expense.description,
            "category": expense.category,
            "subcategory": expense.subcategory,
            "date": expense.date,
            "payment_method": expense.payment_method,
            "is_recurring": expense.is_recurring,
            "notes": expense.notes
        }
        for expense in expenses
    ]


# Budgets
@router.post("/budgets", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_budget(
    name: str,
    amount: float,
    category: str = None,
    period: str = "monthly",
    start_date: str = None,
    end_date: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new budget."""
    db_budget = Budget(
        user_id=current_user.id,
        name=name,
        amount=amount,
        category=category,
        period=period,
        start_date=start_date or datetime.utcnow(),
        end_date=end_date or datetime.utcnow()
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return {"message": "Budget created successfully", "budget_id": db_budget.id}


@router.get("/budgets", response_model=List[dict])
async def get_budgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all budgets for the current user."""
    budgets = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.is_active == True
    ).all()
    
    return [
        {
            "id": budget.id,
            "name": budget.name,
            "amount": float(budget.amount),
            "category": budget.category,
            "period": budget.period,
            "start_date": budget.start_date,
            "end_date": budget.end_date
        }
        for budget in budgets
    ]


# Income
@router.post("/income", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_income(
    amount: float,
    source: str,
    description: str = None,
    is_recurring: bool = False,
    recurring_frequency: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new income record."""
    db_income = Income(
        user_id=current_user.id,
        amount=amount,
        source=source,
        description=description,
        is_recurring=is_recurring,
        recurring_frequency=recurring_frequency
    )
    db.add(db_income)
    db.commit()
    db.refresh(db_income)
    return {"message": "Income recorded successfully", "income_id": db_income.id}


@router.get("/income", response_model=List[dict])
async def get_income(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all income records for the current user."""
    income_records = db.query(Income).filter(
        Income.user_id == current_user.id
    ).order_by(Income.date.desc()).all()
    
    return [
        {
            "id": income.id,
            "amount": float(income.amount),
            "source": income.source,
            "description": income.description,
            "date": income.date,
            "is_recurring": income.is_recurring,
            "recurring_frequency": income.recurring_frequency
        }
        for income in income_records
    ]


# Financial Goals
@router.post("/goals", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_financial_goal(
    name: str,
    target_amount: float,
    current_amount: float = 0,
    target_date: str = None,
    priority: str = "medium",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new financial goal."""
    db_goal = FinancialGoal(
        user_id=current_user.id,
        name=name,
        target_amount=target_amount,
        current_amount=current_amount,
        target_date=target_date,
        priority=priority
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return {"message": "Financial goal created successfully", "goal_id": db_goal.id}


@router.get("/goals", response_model=List[dict])
async def get_financial_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all financial goals for the current user."""
    goals = db.query(FinancialGoal).filter(
        FinancialGoal.user_id == current_user.id
    ).all()
    
    return [
        {
            "id": goal.id,
            "name": goal.name,
            "target_amount": float(goal.target_amount),
            "current_amount": float(goal.current_amount),
            "progress_percentage": (float(goal.current_amount) / float(goal.target_amount)) * 100,
            "target_date": goal.target_date,
            "priority": goal.priority,
            "status": goal.status
        }
        for goal in goals
    ]


@router.put("/goals/{goal_id}/update-amount")
async def update_goal_amount(
    goal_id: int,
    new_amount: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update the current amount for a financial goal."""
    goal = db.query(FinancialGoal).filter(
        FinancialGoal.id == goal_id,
        FinancialGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial goal not found"
        )
    
    goal.current_amount = new_amount
    
    # Check if goal is completed
    if new_amount >= goal.target_amount:
        goal.status = "completed"
    
    db.commit()
    
    return {"message": "Goal amount updated successfully", "new_amount": float(new_amount)}


# Dashboard
@router.get("/dashboard")
async def get_finance_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get finance dashboard data."""
    # Get current month expenses
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year
    
    monthly_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        func.extract('month', Expense.date) == current_month,
        func.extract('year', Expense.date) == current_year
    ).scalar() or 0
    
    # Get monthly income
    monthly_income = db.query(func.sum(Income.amount)).filter(
        Income.user_id == current_user.id,
        func.extract('month', Income.date) == current_month,
        func.extract('year', Income.date) == current_year
    ).scalar() or 0
    
    # Get expenses by category
    category_expenses = db.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        func.extract('month', Expense.date) == current_month,
        func.extract('year', Expense.date) == current_year
    ).group_by(Expense.category).all()
    
    # Get active budgets
    active_budgets = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.is_active == True
    ).all()
    
    # Get financial goals
    goals = db.query(FinancialGoal).filter(
        FinancialGoal.user_id == current_user.id,
        FinancialGoal.status == "active"
    ).all()
    
    return {
        "monthly_summary": {
            "expenses": float(monthly_expenses),
            "income": float(monthly_income),
            "savings": float(monthly_income - monthly_expenses),
            "month": current_month,
            "year": current_year
        },
        "expenses_by_category": [
            {
                "category": category,
                "total": float(total)
            }
            for category, total in category_expenses
        ],
        "active_budgets": len(active_budgets),
        "financial_goals": [
            {
                "name": goal.name,
                "progress": (float(goal.current_amount) / float(goal.target_amount)) * 100,
                "remaining": float(goal.target_amount - goal.current_amount)
            }
            for goal in goals
        ],
        "savings_rate": (float(monthly_income - monthly_expenses) / float(monthly_income)) * 100 if monthly_income > 0 else 0
    }
