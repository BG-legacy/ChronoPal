# ChronoPal Backend

This is the backend service for ChronoPal, a virtual pet application.

## Deployment on Render

This application is configured for deployment on Render.com. The service will automatically:

1. Install dependencies from `requirements.txt`
2. Start the application using Gunicorn with Uvicorn workers

### Manual Deployment Steps

If you need to deploy manually:

1. Make sure you're in the Backend directory
2. Run `pip install -r requirements.txt` to install dependencies
3. Start the application with:
   ```
   gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
   ```

### Local Development

To run the application locally:

1. Install dependencies: `pip install -r requirements.txt`
2. Run the development server: `uvicorn api.main:app --reload`

## Environment Variables

Make sure to set up the following environment variables:
- All necessary MongoDB connection strings
- OpenAI API keys if used
- Other configuration variables as defined in .env

## API Documentation

When the application is running, API documentation is available at:
- Swagger UI: `/docs`
- ReDoc: `/redoc` 