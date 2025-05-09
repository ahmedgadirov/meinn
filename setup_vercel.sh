#!/bin/bash
# Vercel setup script for Meinn Restaurant AI

# Color codes for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Meinn Restaurant AI - Vercel Setup Script${NC}"
echo "This script will help you set up your project for Vercel deployment."
echo

# Check for required commands
echo -e "${YELLOW}Checking required dependencies...${NC}"
commands=("git" "jq")
missing=0

for cmd in "${commands[@]}"; do
  if ! command -v $cmd &> /dev/null; then
    echo -e "${RED}$cmd is not installed. Please install it and try again.${NC}"
    missing=1
  fi
done

if [ $missing -eq 1 ]; then
  echo -e "${RED}Missing dependencies. Please install them and run this script again.${NC}"
  exit 1
fi

echo -e "${GREEN}All dependencies are installed.${NC}"
echo

# Check if this is a git repository
if [ ! -d .git ]; then
  echo -e "${YELLOW}Initializing Git repository...${NC}"
  git init
  echo -e "${GREEN}Git repository initialized.${NC}"
else
  echo -e "${GREEN}Git repository already exists.${NC}"
fi

# Check if Firebase credentials file exists
echo -e "${YELLOW}Checking for Firebase credentials...${NC}"
credential_file="/home/ahmd/Downloads/meinn-aa13d-firebase-adminsdk-fbsvc-106c3608d5.json"

if [ ! -f "$credential_file" ]; then
  echo -e "${RED}Firebase credentials file not found at $credential_file${NC}"
  echo "Please make sure the file exists or update the path in this script."
  exit 1
fi

echo -e "${GREEN}Firebase credentials found.${NC}"
echo

# Create a temporary file for Vercel environment variables
echo -e "${YELLOW}Preparing Vercel environment variables...${NC}"
env_file=".vercel.env"

# Extract credentials as a single line JSON string
creds=$(cat "$credential_file" | jq -c '.')

cat > $env_file << EOL
FIREBASE_PROJECT_ID=meinn-aa13d
FIREBASE_CREDENTIALS_PATH=$credential_file
FIREBASE_CREDENTIALS=$creds
OPENROUTER_API_KEY=your_openrouter_api_key_here
OR_PRIMARY_MODEL=anthropic/claude-3-haiku
OR_FALLBACK_MODEL=mistralai/mixtral-8x7b-instruct
RESTAURANT_NAME=Pizza Inn
ADMIN_API_TOKEN=your_admin_token_here
EOL

echo -e "${GREEN}Environment variables prepared. Check ${YELLOW}.vercel.env${GREEN} file.${NC}"
echo -e "${YELLOW}NOTE: Update the API keys and tokens in this file before deploying.${NC}"
echo

# Check if requirements_vercel.txt exists
if [ -f "requirements_vercel.txt" ]; then
  echo -e "${GREEN}Vercel requirements file found.${NC}"
else
  echo -e "${RED}requirements_vercel.txt not found. Please check your project files.${NC}"
  exit 1
fi

# Add files to git
echo -e "${YELLOW}Adding files to Git...${NC}"
git add vercel.json api firebase_config.py src .gitignore requirements_vercel.txt VERCEL_DEPLOYMENT.md
git status

echo
echo -e "${GREEN}Setup complete! Next steps:${NC}"
echo "1. Review and update API keys in .vercel.env"
echo "2. Commit your changes with: git commit -m \"Prepare for Vercel deployment\""
echo "3. Create a GitHub repository and push your code"
echo "4. Deploy on Vercel following the instructions in VERCEL_DEPLOYMENT.md"
echo
echo -e "${YELLOW}Make sure to add .vercel.env to your .gitignore before pushing to GitHub!${NC}"
