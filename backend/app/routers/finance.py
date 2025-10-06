"""Finance router for managing expenses, budgets, and financial goals."""

from typing import Any, List, Optional
from datetime import datetime
from fastapi import Body

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from ..models.user import User
from ..models.finance import Expense, Budget, Income, FinancialGoal
from app.routers.auth import get_current_user, get_optional_current_user

router = APIRouter()


# Expenses
@router.post("/expenses", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_expense(
    payload: dict = Body(...),
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new expense. Accepts JSON body payload."""
    # Extract and validate fields
    try:
        amount = float(payload.get('amount'))
    except Exception:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='amount is required and must be a number')

    description = payload.get('description')
    category = payload.get('category')
    subcategory = payload.get('subcategory')
    payment_method = payload.get('payment_method')
    is_recurring = bool(payload.get('is_recurring', False))
    recurring_frequency = payload.get('recurring_frequency')
    notes = payload.get('notes')

    db_expense = Expense(
        user_id=(current_user.id if current_user is not None else None),
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
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all expenses for the current user."""
    # Do not return any user's expenses to unauthenticated callers.
    if current_user is None:
        return []
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
    payload: dict = Body(...),
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new budget. Accepts JSON body payload."""
    name = payload.get('name') or payload.get('title') or 'Budget'
    try:
        amount = float(payload.get('amount'))
    except Exception:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='amount is required and must be a number')

    category = payload.get('category')
    # recent data/clients send 'period' while the ORM model uses 'period_type'
    # Normalize both to `period_type` so we don't pass an unexpected kwarg to Budget
    period_type = payload.get('period_type') or payload.get('period') or 'monthly'
    start_date = payload.get('start_date')
    end_date = payload.get('end_date')

    db_budget = Budget(
        user_id=(current_user.id if current_user is not None else None),
        name=name,
        amount=amount,
        category=category,
        period_type=period_type,
        start_date=start_date or datetime.utcnow(),
        end_date=end_date or datetime.utcnow()
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return {"message": "Budget created successfully", "budget_id": db_budget.id}


@router.get("/budgets", response_model=List[dict])
async def get_budgets(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all budgets for the current user."""
    # Do not expose other users' budgets. Return empty list if unauthenticated.
    if current_user is None:
        return []
    budgets = db.query(Budget).filter(Budget.is_active == True, Budget.user_id == current_user.id).all()
    
    return [
        {
            "id": budget.id,
            "name": budget.name,
            "amount": float(budget.amount),
            "category": budget.category,
            "period": budget.period_type,
            "start_date": budget.start_date,
            "end_date": budget.end_date
        }
        for budget in budgets
    ]


# Income
@router.post("/income", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_income(
    payload: dict = Body(...),
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new income record. Accepts JSON body payload."""
    try:
        amount = float(payload.get('amount'))
    except Exception:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='amount is required and must be a number')

    source = payload.get('source')
    description = payload.get('description')
    is_recurring = bool(payload.get('is_recurring', False))
    recurring_frequency = payload.get('recurring_frequency')

    db_income = Income(
        user_id=(current_user.id if current_user is not None else None),
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
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all income records for the current user."""
    # Return no income records to unauthenticated callers.
    if current_user is None:
        return []
    income_records = db.query(Income).filter(Income.user_id == current_user.id).order_by(Income.date_received.desc()).all()
    
    return [
        {
            "id": income.id,
            "amount": float(income.amount),
            "source": income.source,
            "description": income.description,
            "date_received": income.date_received,
            "is_recurring": income.is_recurring,
            "recurring_frequency": income.recurring_frequency
        }
        for income in income_records
    ]


# Financial Goals
@router.post("/goals", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_financial_goal(
    payload: dict = Body(...),
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new financial goal.

    Accept a JSON body for compatibility with frontend clients. Expected keys:
    - target_amount (required, number)
    - title or name (optional)
    - current_amount (optional, defaults to 0)
    - target_date (optional, YYYY-MM-DD string)
    - priority (optional)
    - goal_type (optional, defaults to 'savings')
    """
    # Extract and validate fields from JSON body
    try:
        target_amount = float(payload.get('target_amount'))
    except Exception:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='target_amount is required and must be a number')

    title = payload.get('title') or payload.get('name') or 'Untitled Goal'
    current_amount = float(payload.get('current_amount') or 0)
    priority = payload.get('priority') or 'medium'
    goal_type_final = payload.get('goal_type') or 'savings'

    # Parse target_date if provided
    parsed_target_date = None
    td = payload.get('target_date')
    if td:
        try:
            from datetime import datetime as _dt

            if isinstance(td, str):
                parsed_target_date = _dt.strptime(td, "%Y-%m-%d").date()
            else:
                parsed_target_date = td
        except Exception:
            parsed_target_date = None

    db_goal = FinancialGoal(
        user_id=(current_user.id if current_user is not None else None),
        title=title,
        goal_type=goal_type_final,
        target_amount=target_amount,
        current_amount=current_amount,
        target_date=parsed_target_date,
        priority=priority
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return {"message": "Financial goal created successfully", "goal_id": db_goal.id}


@router.get("/goals", response_model=List[dict])
async def get_financial_goals(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all financial goals for the current user."""
    # Do not reveal other users' goals to unauthenticated callers.
    if current_user is None:
        return []
    goals = db.query(FinancialGoal).filter(FinancialGoal.user_id == current_user.id).all()
    
    return [
        {
            "id": goal.id,
            "title": goal.title,
            "description": goal.description,
            "goal_type": goal.goal_type,
            "target_amount": float(goal.target_amount),
            "current_amount": float(goal.current_amount),
            "progress_percentage": goal.progress_percentage,
            "remaining_amount": goal.remaining_amount,
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
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update the current amount for a financial goal."""
    query = db.query(FinancialGoal).filter(FinancialGoal.id == goal_id)
    if current_user is not None:
        query = query.filter(FinancialGoal.user_id == current_user.id)
    goal = query.first()
    
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
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get finance dashboard data."""
    # Dashboard requires authentication to avoid exposing aggregated data across users.
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year

    expense_filters = [func.extract('month', Expense.date) == current_month,
                       func.extract('year', Expense.date) == current_year,
                       Expense.user_id == current_user.id]
    monthly_expenses = db.query(func.sum(Expense.amount)).filter(*expense_filters).scalar() or 0

    income_filters = [func.extract('month', Income.date_received) == current_month,
                      func.extract('year', Income.date_received) == current_year,
                      Income.user_id == current_user.id]
    monthly_income = db.query(func.sum(Income.amount)).filter(*income_filters).scalar() or 0
    
    # Get expenses by category
    category_filters = [func.extract('month', Expense.date) == current_month,
                        func.extract('year', Expense.date) == current_year]
    if current_user is not None:
        category_filters.insert(0, Expense.user_id == current_user.id)
    category_expenses = db.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter(*category_filters).group_by(Expense.category).all()
    
    # Get active budgets
    active_budgets = db.query(Budget).filter(Budget.is_active == True, Budget.user_id == current_user.id).all()
    
    # Get financial goals
    goals = db.query(FinancialGoal).filter(FinancialGoal.status == "active", FinancialGoal.user_id == current_user.id).all()
    
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
                # Some older code expected `name`; the model uses `title`.
                "name": getattr(goal, 'title', None) or getattr(goal, 'name', None) or "",
                "progress": (float(goal.current_amount) / float(goal.target_amount)) * 100 if goal.target_amount else 0,
                "remaining": float(goal.target_amount - goal.current_amount) if goal.target_amount else 0.0
            }
            for goal in goals
        ],
        "savings_rate": (float(monthly_income - monthly_expenses) / float(monthly_income)) * 100 if monthly_income > 0 else 0
    }
