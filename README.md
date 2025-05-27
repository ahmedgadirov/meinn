# Meinn - AI-Powered Restaurant Menu Assistant

Meinn is an intelligent AI-powered chatbot designed specifically for restaurant menu interactions, built on the successful Elchi AI framework. It provides an engaging, personalized experience for restaurant customers while offering powerful tools for restaurant owners to manage their menus, track orders, and understand customer preferences.

## 🍽️ Key Features

### Customer Experience
- **AI-Powered Recommendations:** Suggests meals based on past orders, time of day, and current trends
- **Smart Pairing:** Recommends drinks or side dishes based on main orders
- **Multilingual Support:** Seamless language switching for international customers (Azerbaijani, English, Russian, Turkish, Arabic, Hindi, French, Italian)
- **Real-Time Availability:** Shows only available menu items based on restaurant inventory
- **User-Friendly Chat Interface:** Natural conversational experience for browsing menus and placing orders

### Restaurant Management
- **Comprehensive Admin Panel:** Dashboard with sales trends, popular dishes, and AI performance metrics
- **Menu Management:** Add, edit, delete menu items with images and dynamic pricing
- **Order Management:** Real-time order tracking with accept/reject functionality
- **AI Customization:** Train AI responses for FAQs and personalized customer interactions
- **Analytics & Reports:** Detailed insights into customer preferences and ordering patterns

## 🚀 Tech Stack

- **Frontend:** React with Next.js for SSR
- **UI:** Tailwind CSS / Shadcn/UI for modern, responsive interfaces
- **Backend:** Flask/FastAPI for core functionality
- **Database:** PostgreSQL/Firebase for data storage
- **State Management:** Zustand/Redux for chatbot interactions
- **Real-Time Features:** WebSockets for live updates

## 🛠️ Installation & Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/meinn.git
cd meinn
```

2. Run the unified setup script with your preferred data processing option
```bash
# Default: Uses binary wheels for pandas/numpy
./run.sh

# Standard: Uses regular pandas/numpy installation (may require compiler)
./run.sh standard

# Polars: Uses polars instead of pandas/numpy (no compilation required)
./run.sh polars
```

The script will:
- Create a virtual environment
- Install appropriate dependencies 
- Initialize the database
- Start the application

3. Set up environment variables (if not already configured)
```bash
cp .env.example .env
# Edit .env with your configuration
```

See [REQUIREMENTS_INFO.md](REQUIREMENTS_INFO.md) for detailed information about the requirements structure and installation options.

## 🧠 AI Configuration

Meinn uses OpenRouter to access various language models:
- Primary: Claude 3 Haiku (anthropic/claude-3-haiku)
- Fallback: Mixtral 8x7B (mistralai/mixtral-8x7b-instruct)
- Backup: Llama 2 70B (meta-llama/llama-2-70b-chat)

## 📋 Admin Panel Access

Access the admin panel at `http://localhost:5050/admin` with the credentials set in your `.env` file.

## 🌐 Languages Supported

- 🇦🇿 Azerbaijani (Primary)
- 🇬🇧 English
- 🇷🇺 Russian
- 🇹🇷 Turkish
- 🇸🇦 Arabic
- 🇮🇳 Hindi
- 🇫🇷 French
- 🇮🇹 Italian

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

Meinn is built on the foundation of the Elchi AI framework, adapting its proven capabilities for restaurant-specific applications.

---

© 2025 Pizza Inn. All Rights Reserved.
