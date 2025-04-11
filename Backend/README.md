# ChronoPal Backend

This is the backend service for ChronoPal, a virtual pet application.

## Deployment on Vercel

This application is configured for deployment on Vercel. To deploy:

1. Install the Vercel CLI: `npm i -g vercel`
2. Login to Vercel: `vercel login`
3. Deploy the application: 
   ```
   cd path/to/Backend
   vercel
   ```

4. To deploy to production: `vercel --prod`

### Environment Variables

Make sure to set up the following environment variables in your Vercel project settings:
- MONGODB_URI: Your MongoDB connection string
- MONGODB_DB_NAME: Your MongoDB database name
- OPENAI_API_KEY: Your OpenAI API key

### Local Development

To run the application locally:

1. Install dependencies: `pip install -r requirements.txt`
2. Run the development server: `uvicorn api.main:app --reload`

## API Documentation

When the application is running, API documentation is available at:
- Swagger UI: `/docs`
- ReDoc: `/redoc` 