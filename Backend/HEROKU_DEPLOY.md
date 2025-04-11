# Deploying to Heroku

This guide will help you deploy the ChronoPal backend to Heroku.

## Prerequisites

1. [Heroku Account](https://signup.heroku.com/)
2. [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. Git

## Steps to Deploy

### 1. Login to Heroku

```bash
heroku login
```

### 2. Create a Heroku App

```bash
heroku create chronopal-backend
```

### 3. Configure MongoDB

Add the MongoDB Atlas add-on or set up your own MongoDB database:

```bash
# Option 1: Use MongoDB Atlas directly
heroku config:set MONGODB_URI="your_mongodb_atlas_connection_string"
heroku config:set MONGODB_DB_NAME="chronopal"

# Option 2: Use Heroku add-on (MongoDB Atlas)
heroku addons:create mongodbatlas:free
```

### 4. Set Environment Variables

Make sure to set all required environment variables:

```bash
heroku config:set OPENAI_API_KEY="your_openai_api_key"
heroku config:set ENVIRONMENT="production"
```

### 5. Deploy Your Code

Push your code to Heroku:

```bash
git subtree push --prefix Backend heroku main
```

Or, if you're only deploying the Backend folder:

```bash
git init
git add .
git commit -m "Initial Heroku deployment"
heroku git:remote -a chronopal-backend
git push heroku main
```

### 6. Verify Deployment

```bash
heroku open
```

Navigate to `/api/test-mongodb` to verify MongoDB connection.

### 7. Check Logs

```bash
heroku logs --tail
```

## MongoDB Atlas Setup

If you're using MongoDB Atlas directly instead of the Heroku add-on:

1. Create a cluster on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Set up a database user with read/write permissions
3. Whitelist all IP addresses (0.0.0.0/0) for access or just Heroku's IPs
4. Get the connection string and replace `<password>` with your database user's password
5. Set the connection string in Heroku config vars as MONGODB_URI

## Troubleshooting

- **Application Error**: Check Heroku logs for details
- **Database Connection Issues**: Verify MongoDB URI is correctly set
- **Port Binding Errors**: Ensure the app is using `process.env.PORT` 