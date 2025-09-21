# Dristhi - Vercel Deployment Guide

This guide will help you deploy the Dristhi application (both frontend and backend) to Vercel.

## Prerequisites

1. A Vercel account (sign up at https://vercel.com if you don't have one)
2. Vercel CLI installed (optional but recommended)
   ```
   npm install -g vercel
   ```
3. Git repository for your project (recommended)

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

## Deploying the Backend

Note: Vercel is primarily designed for frontend applications. For the backend, we're using a serverless approach, but you may need to adapt your backend further depending on its complexity.

1. Navigate to your backend directory:
   ```
   cd backend
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
   - Select the backend directory as the root
   - Configure the project:
     - Framework Preset: Other
     - Build Command: pip install -r requirements.txt
     - Output Directory: (leave empty)
   - Deploy

## Environment Variables

Make sure to set up your environment variables in the Vercel dashboard:

1. Go to your project settings in Vercel
2. Navigate to the "Environment Variables" tab
3. Add all the environment variables from your .env files
   - For the frontend: API endpoints, authentication keys, etc.
   - For the backend: Database connection strings, API keys, etc.

## Connecting Frontend and Backend

After deploying both parts:

1. Get the deployment URL for your backend (e.g., https://dristhi-backend.vercel.app)
2. Update the frontend's vercel.json file to point to your backend URL:
   ```json
   {
     "routes": [
       {
         "src": "/api/(.*)",
         "dest": "https://your-backend-url.vercel.app/api/$1"
       }
     ]
   }
   ```
3. Redeploy your frontend

## Important Notes

1. Database connections: If your backend uses a database, make sure it's accessible from Vercel's serverless functions. Consider using a cloud database service.
2. Serverless limitations: Vercel's serverless functions have certain limitations (execution time, memory, etc.). You may need to optimize your backend accordingly.
3. Cold starts: Serverless functions may experience "cold starts" which can cause initial delays.

## Troubleshooting

- Check Vercel deployment logs for any errors
- Ensure all environment variables are correctly set
- Verify that your backend endpoints are correctly configured in the frontend
- For database issues, confirm your connection strings and network access settings

## Next Steps

After deployment, monitor your application's performance and make adjustments as needed. Consider setting up CI/CD pipelines for automated deployments.