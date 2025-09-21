# Dristhi - Deployment Guide

This guide will help you deploy the Dristhi application with the frontend on Vercel and the backend on Render.

## Prerequisites

1. A Vercel account (sign up at https://vercel.com if you don't have one)
2. A Render account (sign up at https://render.com if you don't have one)
3. Vercel CLI installed (optional but recommended)
   ```
   npm install -g vercel
   ```
4. Git repository for your project (recommended)

## Deploying the Frontend

1. Navigate to your frontend directory:
   ```
   cd frontend
   ```

2. Login to Vercel (if using CLI):
   ```
   vercel login
   ```

3. Deploy to Vercel:
   ```
   vercel
   ```
   
   Or deploy directly from the Vercel dashboard:
   - Go to https://vercel.com/new
   - Import your Git repository
   - Select the frontend directory as the root
   - Configure the project:
     - Framework Preset: Vite
     - Build Command: npm run build
     - Output Directory: dist
   - Deploy

## Deploying the Backend to Render

For the backend, we'll use Render which is better suited for Python/FastAPI applications:

1. Log in to your Render account at https://dashboard.render.com/

2. Create a new Web Service:
   - Click "New" and select "Web Service"
   - Connect your Git repository
   - Select the backend directory as the root

3. Configure the service:
   - Name: dristhi-backend (or your preferred name)
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Select the appropriate plan (Free tier works for testing)

4. Add Environment Variables:
   - Click on "Environment" and add all variables from your backend .env file
   - Make sure to update database URLs and other connection strings for production

5. Deploy the service by clicking "Create Web Service"

## Environment Variables

Make sure to set up your environment variables in the Vercel dashboard:

1. Go to your project settings in Vercel
2. Navigate to the "Environment Variables" tab
3. Add all the environment variables from your .env files
   - For the frontend: API endpoints, authentication keys, etc.
   - For the backend: Database connection strings, API keys, etc.

## Connecting Frontend (Vercel) and Backend (Render)

After deploying both parts:

1. Get the deployment URL for your Render backend (e.g., https://dristhi-backend.onrender.com)
2. Update the frontend's environment variables in Vercel:
   - Go to your frontend project in the Vercel dashboard
   - Navigate to "Settings" > "Environment Variables"
   - Add or update `VITE_API_BASE_URL` with your Render backend URL

3. Update the frontend's vercel.json file to point to your Render backend URL:
   ```json
   {
     "routes": [
       {
         "src": "/api/(.*)",
         "dest": "https://your-render-backend-url.onrender.com/api/$1"
       }
     ]
   }
   ```

4. Update the CORS settings in your backend .env file on Render:
   - Add your Vercel frontend URL to the `BACKEND_CORS_ORIGINS` list
   - Example: `BACKEND_CORS_ORIGINS=["https://your-frontend-url.vercel.app","http://localhost:3000"]`

5. Redeploy your frontend on Vercel

## Important Notes

1. Database connections: For your Render backend, use a cloud database service like Render's PostgreSQL, Railway, or Supabase that's accessible from Render's servers.

2. Environment variables: Make sure to set all required environment variables in both Vercel (for frontend) and Render (for backend).

3. Cold starts: The free tier of Render has cold starts, meaning your backend may take a moment to respond after periods of inactivity.

4. Custom domains: Both Vercel and Render allow you to set up custom domains for your applications.

5. Render limitations: Be aware of Render's free tier limitations on bandwidth, compute hours, and build minutes.

## Troubleshooting

- Check Vercel deployment logs for any errors
- Ensure all environment variables are correctly set
- Verify that your backend endpoints are correctly configured in the frontend
- For database issues, confirm your connection strings and network access settings

## Next Steps

After deployment, monitor your application's performance and make adjustments as needed. Consider setting up CI/CD pipelines for automated deployments.