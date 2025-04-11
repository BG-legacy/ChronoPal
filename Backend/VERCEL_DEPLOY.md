# Deploying ChronoPal to Vercel

This guide will help you deploy the ChronoPal backend to Vercel.

## Prerequisites

1. A [Vercel](https://vercel.com/) account
2. A MongoDB Atlas account and database (URI should be in your .env file)
3. Git installed on your local machine

## Deployment Steps

### Option 1: Deploy from GitHub

1. Push your code to a GitHub repository
2. Log in to Vercel and click "New Project"
3. Import your GitHub repository
4. Configure the project:
   - Set the framework preset to "Other"
   - Set the root directory to "Backend"
   - Set the build command to `pip install -r requirements.txt`
   - Set the output directory to `.`
   - Set the install command to `pip install -r requirements.txt`
   - Set the development command to `uvicorn api.vercel_app:app --host 0.0.0.0 --port 3000`

5. Add environment variables:
   - `MONGODB_URI`: Your MongoDB connection string
   - `MONGODB_DB_NAME`: Your MongoDB database name
   - `OPENAI_API_KEY`: Your OpenAI API key

6. Click "Deploy"

### Option 2: Deploy from CLI

1. Install the Vercel CLI:
   ```
   npm i -g vercel
   ```

2. Login to Vercel:
   ```
   vercel login
   ```

3. Navigate to your Backend directory:
   ```
   cd path/to/ChronoPal/Backend
   ```

4. Deploy:
   ```
   vercel
   ```

5. Follow the prompts to configure your project
   - Link to existing project if you've deployed before
   - Set the environment variables when prompted

6. Deploy to production:
   ```
   vercel --prod
   ```

## Verifying Your Deployment

After deployment, your API will be available at:
`https://your-project-name.vercel.app/api`

You can test it with:
`https://your-project-name.vercel.app/api/health`

## Troubleshooting

If you encounter the BSON import error:
- Make sure you're not using the standalone `bson` package
- Only use the BSON that comes with PyMongo

If you have session issues:
- Remember that Vercel functions are stateless
- Consider storing sessions in MongoDB instead

## Important Notes

1. Vercel deploys serverless functions, so your API endpoints become individual functions
2. Global variables won't persist between invocations of different functions
3. MongoDB connections are optimized for serverless environment (see VERCEL_MONGODB.md) 