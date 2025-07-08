# Wallie Voice Assistant Integration

This document explains how to integrate the Python voice assistant (`test.py`) with your Next.js shopping application to fetch products from the database and add items to cart.

## Overview

The integration consists of:
1. **Next.js API endpoints** - To serve products and handle cart operations
2. **Python voice assistant** - Enhanced to fetch data from your database
3. **Database integration** - Real-time product fetching from your PostgreSQL database

## Architecture

```
┌─────────────────┐    HTTP API    ┌─────────────────┐    Database    ┌─────────────────┐
│  Voice Assistant │  ◄─────────►   │  Next.js App    │  ◄─────────►   │  PostgreSQL DB  │
│    (test.py)    │                │   API Routes    │                │   (via Drizzle) │
└─────────────────┘                └─────────────────┘                └─────────────────┘
```

## Setup Instructions

### Prerequisites
- Python 3.8+ installed
- Node.js 18+ installed
- PostgreSQL database configured
- Microphone access for speech recognition

### Step 1: Install Dependencies

#### Python Dependencies
```powershell
pip install -r requirements.txt
```

#### Node.js Dependencies
```powershell
npm install
```

### Step 2: Database Setup

1. Make sure your `.env.local` file has the correct database URL:
```
NEXT_PUBLIC_DRIZZLE_DB_URL=your-postgresql-connection-string
```

2. Push the database schema:
```powershell
npm run db:push
```

3. Seed the database with products:
```powershell
node lib/seed.js
```

### Step 3: Configuration

1. Copy the configuration template:
```powershell
copy config_template.py config.py
```

2. Update `config.py` with your settings:
```python
# Your Gemini API key
GEMINI_API_KEY = "your-actual-api-key-here"

# Next.js app URL (change for production)
BASE_URL = "http://localhost:3000"

# Email for voice assistant purchases
DEFAULT_USER_EMAIL = "voice-assistant@example.com"
```

### Step 4: Run the Application

1. Start the Next.js development server:
```powershell
npm run dev
```

2. In another terminal, run the voice assistant:
```powershell
python test.py
```

## API Endpoints

### GET /api/products
Returns all products from the database.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Wireless Headphones",
    "description": "High-quality wireless headphones",
    "price": "199.99",
    "imageUrl": "/products/headphones.png",
    "category": "Electronics"
  }
]
```

### POST /api/voice-cart
Adds items to cart for voice assistant purchases.

**Request:**
```json
{
  "productId": 1,
  "email": "voice-assistant@example.com",
  "quantity": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "Item added to cart successfully",
  "product": { ... }
}
```

## Voice Assistant Features

### Dynamic Product Loading
- Fetches products from database on startup
- Falls back to hardcoded products if API fails
- Supports product search by name, description, or category

### Conversation Flow
1. **Greeting** - Welcome and product listing
2. **Product Inquiry** - Customer asks about specific products
3. **Details** - Gather quantity and preferences
4. **Checkout** - Add to cart and complete purchase

### Hinglish Support
The assistant speaks in Hinglish (Hindi + English) for natural conversation with Indian customers.

## Troubleshooting

### Common Issues

1. **"Import speech_recognition could not be resolved"**
   - Install: `pip install speech-recognition`

2. **"Failed to fetch products"**
   - Ensure Next.js server is running on port 3000
   - Check database connection
   - Verify API endpoint is accessible

3. **"Failed to add to cart"**
   - Check database connection
   - Verify product exists in database
   - Check API endpoint logs

4. **Speech recognition not working**
   - Check microphone permissions
   - Ensure microphone is connected
   - Test with: `python -c "import speech_recognition; print('OK')"`

### Logs
Both applications provide detailed logging:
- Voice assistant: Console output with timestamps
- Next.js: Check browser console and terminal

## Customization

### Adding New Products
Products are stored in the database. You can:
1. Add via the web interface (if available)
2. Modify `lib/seed.js` and re-run seeding
3. Add directly to the database

### Modifying Voice Responses
Update the prompt templates in the `_get_prompt_template` method in `test.py`.

### Changing User Email
Update `DEFAULT_USER_EMAIL` in `config.py` to associate voice purchases with a specific user.

## Production Considerations

1. **Security**
   - Use environment variables for API keys
   - Implement proper authentication for voice-cart endpoint
   - Add rate limiting

2. **Scalability**
   - Consider caching product data
   - Implement connection pooling
   - Add error retry mechanisms

3. **Monitoring**
   - Add application monitoring
   - Log all transactions
   - Monitor API response times

## File Structure

```
wallie-shopping-assistant/
├── test.py                 # Voice assistant (updated)
├── requirements.txt        # Python dependencies
├── config_template.py      # Configuration template
├── config.py              # Your configuration (create from template)
├── setup.ps1              # Setup script
├── app/
│   └── api/
│       ├── products/
│       │   └── route.js    # Products API endpoint
│       └── voice-cart/
│           └── route.js    # Voice cart API endpoint
└── ... (existing Next.js files)
```

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs for error messages
3. Ensure all dependencies are installed
4. Verify database connectivity
