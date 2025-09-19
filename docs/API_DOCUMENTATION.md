# Dristhi API Documentation

## Overview

This document provides detailed information about the Dristhi API endpoints, request/response formats, and usage examples. The Dristhi API is built using FastAPI and follows RESTful principles.

## Base URL

```
http://localhost:8000/api/v1
```

For production deployments, replace `localhost:8000` with your domain.

## Authentication

Most API endpoints require authentication using JWT (JSON Web Token). Include the token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

### Authentication Endpoints

#### Login

```
POST /auth/login
```

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Register

```
POST /auth/register
```

**Request Body:**

```json
{
  "name": "John Doe",
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "user@example.com",
  "created_at": "2023-06-15T10:30:00"
}
```

## Career Module

### Career Goals

#### Get All Career Goals

```
GET /career/goals
```

**Query Parameters:**

- `status_filter` (optional): Filter goals by status ("active", "completed", "all")

**Response:**

```json
[
  {
    "id": 1,
    "title": "Learn Python Programming",
    "description": "Master Python for data science and web development",
    "target_date": "2023-12-31T00:00:00",
    "priority": "high",
    "status": "active",
    "progress": 35.0,
    "user_id": 1,
    "created_at": "2023-06-01T09:00:00",
    "updated_at": "2023-06-15T14:30:00"
  },
  {
    "id": 2,
    "title": "Complete AWS Certification",
    "description": "Get AWS Solutions Architect certification",
    "target_date": "2023-09-30T00:00:00",
    "priority": "medium",
    "status": "active",
    "progress": 20.0,
    "user_id": 1,
    "created_at": "2023-06-05T11:00:00",
    "updated_at": "2023-06-10T16:45:00"
  }
]
```

#### Get Career Goal by ID

```
GET /career/goals/{goal_id}
```

**Response:**

```json
{
  "id": 1,
  "title": "Learn Python Programming",
  "description": "Master Python for data science and web development",
  "target_date": "2023-12-31T00:00:00",
  "priority": "high",
  "status": "active",
  "progress": 35.0,
  "user_id": 1,
  "created_at": "2023-06-01T09:00:00",
  "updated_at": "2023-06-15T14:30:00"
}
```

#### Create Career Goal

```
POST /career/goals
```

**Request Body:**

```json
{
  "title": "Learn Machine Learning",
  "description": "Study ML algorithms and implement projects",
  "target_date": "2023-12-31T00:00:00",
  "priority": "high",
  "status": "active"
}
```

**Response:**

```json
{
  "id": 3,
  "title": "Learn Machine Learning",
  "description": "Study ML algorithms and implement projects",
  "target_date": "2023-12-31T00:00:00",
  "priority": "high",
  "status": "active",
  "progress": 0.0,
  "user_id": 1,
  "created_at": "2023-06-20T10:15:00",
  "updated_at": "2023-06-20T10:15:00"
}
```

#### Update Career Goal

```
PUT /career/goals/{goal_id}
```

**Request Body:**

```json
{
  "title": "Learn Advanced Machine Learning",
  "priority": "medium",
  "progress": 15.0
}
```

**Response:**

```json
{
  "id": 3,
  "title": "Learn Advanced Machine Learning",
  "description": "Study ML algorithms and implement projects",
  "target_date": "2023-12-31T00:00:00",
  "priority": "medium",
  "status": "active",
  "progress": 15.0,
  "user_id": 1,
  "created_at": "2023-06-20T10:15:00",
  "updated_at": "2023-06-20T11:30:00"
}
```

## Habits Module

### Habits

#### Get All Habits

```
GET /habits
```

**Query Parameters:**

- `status` (optional): Filter habits by status ("active", "completed", "all")
- `category` (optional): Filter habits by category

**Response:**

```json
[
  {
    "id": 1,
    "name": "Morning Meditation",
    "description": "15 minutes of mindfulness meditation",
    "category": "wellness",
    "frequency": "daily",
    "time_of_day": "morning",
    "streak": 7,
    "status": "active",
    "user_id": 1,
    "created_at": "2023-06-01T08:00:00",
    "updated_at": "2023-06-15T08:15:00"
  },
  {
    "id": 2,
    "name": "Read Technical Books",
    "description": "Read technical books for 30 minutes",
    "category": "learning",
    "frequency": "daily",
    "time_of_day": "evening",
    "streak": 5,
    "status": "active",
    "user_id": 1,
    "created_at": "2023-06-02T20:00:00",
    "updated_at": "2023-06-15T21:00:00"
  }
]
```

## Finance Module

### Expenses

#### Get All Expenses

```
GET /finance/expenses
```

**Query Parameters:**

- `start_date` (optional): Filter expenses from this date (YYYY-MM-DD)
- `end_date` (optional): Filter expenses until this date (YYYY-MM-DD)
- `category` (optional): Filter expenses by category

**Response:**

```json
[
  {
    "id": 1,
    "amount": 500.0,
    "category": "food",
    "description": "Grocery shopping",
    "date": "2023-06-10T18:30:00",
    "payment_method": "credit_card",
    "user_id": 1,
    "created_at": "2023-06-10T19:00:00",
    "updated_at": "2023-06-10T19:00:00"
  },
  {
    "id": 2,
    "amount": 1200.0,
    "category": "education",
    "description": "Online course subscription",
    "date": "2023-06-12T10:15:00",
    "payment_method": "upi",
    "user_id": 1,
    "created_at": "2023-06-12T10:20:00",
    "updated_at": "2023-06-12T10:20:00"
  }
]
```

## Mood Module

### Mood Logs

#### Get Mood Logs

```
GET /mood/logs
```

**Query Parameters:**

- `start_date` (optional): Filter logs from this date (YYYY-MM-DD)
- `end_date` (optional): Filter logs until this date (YYYY-MM-DD)

**Response:**

```json
[
  {
    "id": 1,
    "mood_score": 8,
    "notes": "Feeling productive and energetic",
    "factors": ["good_sleep", "exercise", "social_interaction"],
    "date": "2023-06-15T08:00:00",
    "user_id": 1,
    "created_at": "2023-06-15T08:05:00",
    "updated_at": "2023-06-15T08:05:00"
  },
  {
    "id": 2,
    "mood_score": 6,
    "notes": "Slightly stressed about project deadline",
    "factors": ["work_pressure", "lack_of_sleep"],
    "date": "2023-06-16T08:00:00",
    "user_id": 1,
    "created_at": "2023-06-16T08:10:00",
    "updated_at": "2023-06-16T08:10:00"
  }
]
```

## AI Services

### Career Advice

```
POST /ai/career/advice
```

**Request Body:**

```json
{
  "query": "What skills should I learn for a career in data science?",
  "context": {
    "current_skills": ["Python basics", "SQL"],
    "career_goals": ["Become a data scientist in 2 years"],
    "industry_preference": "Technology"
  }
}
```

**Response:**

```json
{
  "advice": "Based on your current skills and goals, I recommend focusing on these key areas for a data science career:\n\n1. **Advanced Python Programming** - Build on your basics with libraries like NumPy, Pandas, and Scikit-learn\n2. **Statistics and Probability** - Essential mathematical foundations\n3. **Machine Learning Algorithms** - Understanding how different algorithms work\n4. **Data Visualization** - Using tools like Matplotlib, Seaborn, or Tableau\n5. **Big Data Technologies** - Spark, Hadoop basics\n\nI suggest starting with strengthening your Python skills through data analysis projects, then moving into machine learning fundamentals.",
  "recommended_resources": [
    {
      "title": "Python for Data Science Handbook",
      "type": "book",
      "url": "https://jakevdp.github.io/PythonDataScienceHandbook/"
    },
    {
      "title": "StatQuest with Josh Starmer",
      "type": "youtube",
      "url": "https://www.youtube.com/c/joshstarmer"
    }
  ],
  "next_steps": [
    "Complete a Python for data analysis course",
    "Build a portfolio project analyzing a public dataset",
    "Learn the fundamentals of machine learning algorithms"
  ]
}
```

## Error Responses

The API uses standard HTTP status codes to indicate the success or failure of requests.

### Common Error Codes

- `400 Bad Request`: Invalid request parameters or body
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Authenticated but not authorized to access the resource
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server-side error

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

For validation errors:

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Pagination

Endpoints that return lists of items support pagination using query parameters:

- `page`: Page number (default: 1)
- `limit`: Number of items per page (default: 20, max: 100)

Paginated responses include metadata:

```json
{
  "items": [...],
  "total": 45,
  "page": 1,
  "limit": 20,
  "pages": 3
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse. Limits are:

- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users

When rate limited, the API returns a `429 Too Many Requests` status code.

## API Documentation

Interactive API documentation is available at:

- Swagger UI: `/api/v1/docs`
- ReDoc: `/api/v1/redoc`