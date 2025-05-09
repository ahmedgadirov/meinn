# Vercel Deployment Guide for Meinn Restaurant AI

This guide will walk you through deploying the Meinn Restaurant AI application to Vercel using GitHub integration.

## Prerequisites

- GitHub account
- Vercel account (can sign up with GitHub)
- Firebase project (`meinn-aa13d`)
- Firebase Admin SDK credentials file (`meinn-aa13d-firebase-adminsdk-fbsvc-106c3608d5.json`)

## Setup Process

### 1. GitHub Setup

1. Create a new GitHub repository:
   ```bash
   cd meinn-main
   git init
   git add .
   git commit -m "Initial commit for Vercel deployment"
   ```

2. Create a repository on GitHub

3. Connect your local repository to GitHub:
   ```bash
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

### 2. Vercel Setup

1. Log in to [Vercel](https://vercel.com)

2. Click "Add New..." → "Project"

3. Import your GitHub repository:
   - Connect your GitHub account if not already connected
   - Select the repository you just created
   - Click "Import"

4. Configure the project:
   - **Project Name:** Choose a name (e.g., "meinn")
   - **Framework Preset:** Select "Other"
   - **Root Directory:** `./`
   - **Build Command:** Leave blank (handled by Vercel's Python builder)
   - **Output Directory:** Leave blank

5. Set up environment variables:
   - `FIREBASE_PROJECT_ID`: `meinn-aa13d`
   - `FIREBASE_CREDENTIALS`: (Copy the entire contents of the credentials JSON file as a single line string)
   - `OPENROUTER_API_KEY`: Your OpenRouter API key
   - `OR_PRIMARY_MODEL`: `anthropic/claude-3-haiku`
   - `OR_FALLBACK_MODEL`: `mistralai/mixtral-8x7b-instruct`
   - `RESTAURANT_NAME`: `Pizza Inn` (or your restaurant name)
   - `ADMIN_API_TOKEN`: Choose a secure token for admin operations

6. Click "Deploy"

### 3. Handling Firebase Credentials

For the `FIREBASE_CREDENTIALS` environment variable, you need to:

1. Open the Firebase credentials file (`meinn-aa13d-firebase-adminsdk-fbsvc-106c3608d5.json`)
2. Copy the entire contents
3. Paste it as a string in the environment variable field in Vercel
4. Make sure it's properly formatted as a single line (no line breaks)

### 4. Verifying the Deployment

1. Once deployed, Vercel will provide a URL for your application (e.g., `https://meinn.vercel.app`)

2. Test the endpoints:
   - Visit the home page (`/`)
   - Check the API health endpoint (`/health`)
   - Test menu endpoints (`/api/menu/items`)

### 5. Setting Up Custom Domain (Optional)

1. In the Vercel dashboard, go to your project
2. Click "Settings" → "Domains"
3. Add your custom domain and follow the DNS instructions

## Updating the Application

With GitHub + Vercel integration, updating your application is simple:

1. Make changes to your code locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your update message"
   git push
   ```
3. Vercel will automatically deploy the changes

## Monitoring and Logs

1. In the Vercel dashboard, go to your project
2. Click "Deployments" to see all deployments
3. Select a deployment to view logs and details

## Troubleshooting

If you encounter issues:

1. Check the build and deployment logs in Vercel
2. Verify your environment variables are set correctly
3. Ensure Firebase permissions are properly configured
4. Check for any errors in the Function Logs
