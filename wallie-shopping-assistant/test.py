import os
import re
import time
import json
import uuid
import logging
from typing import Dict, List, Any

# HTTP client for API calls
import requests

# Speech recognition and text-to-speech
import speech_recognition as sr
from gtts import gTTS
import pygame

# Gemini AI
import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure Gemini API
try:
    from config import GEMINI_API_KEY, BASE_URL, DEFAULT_USER_EMAIL
except ImportError:
    # Fallback to default values if config.py doesn't exist
    GEMINI_API_KEY = 'AIzaSyDFDvNpAWn56sdEmkH2X_sXCoPftat7zqg'  # Replace with your actual key
    BASE_URL = "http://localhost:3000"
    DEFAULT_USER_EMAIL = "voice-assistant@example.com"

genai.configure(api_key=GEMINI_API_KEY)

# Configuration for Next.js application
PRODUCTS_API_URL = f"{BASE_URL}/api/products"
VOICE_CART_API_URL = f"{BASE_URL}/api/voice-cart"


class SpeechHandler:
    """Handles speech recognition and text-to-speech functionality."""
    
    def __init__(self, language: str = "en-IN", tld: str = "co.in"):
        """Initialize speech handler."""
        self.language = language
        self.tld = tld
        self.recognizer = sr.Recognizer()
        
        # Configure speech recognition settings
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.8
        
        # Initialize pygame for audio playback
        pygame.mixer.init()
        logger.info("Speech handler initialized")
    
    def recognize_speech(self) -> str:
        """Capture voice input and convert to text."""
        with sr.Microphone() as source:
            logger.info("Listening...")
            print("Listening...")
            
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                # Listen for audio input
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                logger.info("Processing speech...")
                
                # Convert speech to text
                text = self.recognizer.recognize_google(audio, language=self.language)
                logger.info(f"Customer: {text}")
                print(f"Customer: {text}")
                
                return text.lower()
                
            except sr.UnknownValueError:
                logger.warning("Could not understand audio")
                print("Sorry, I didn't catch that.")
            except sr.RequestError as e:
                logger.error(f"Speech service error: {e}")
                print("Speech service error. Please try again.")
            except sr.WaitTimeoutError:
                logger.warning("No speech detected within timeout period")
                print("I didn't hear anything. Please try again.")
                
        return ""
    
    def speak(self, text: str, slow: bool = False) -> None:
        """Convert text to speech and play it."""
        # Clean text for TTS
        cleaned_text = re.sub(r'[^\w\s.,!?-]', '', text)
        logger.info(f"AI: {cleaned_text}")
        print(f"AI: {cleaned_text}")
        
        # Generate TTS audio
        filename = f"response_{uuid.uuid4().hex[:8]}.mp3"
        try:
            tts = gTTS(text=cleaned_text, lang=self.language.split('-')[0], 
                      slow=slow, tld=self.tld)
            tts.save(filename)
            
            # Play audio
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            
            # Wait for audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
        except Exception as e:
            logger.error(f"TTS error: {e}")
            print(f"Error generating speech: {e}")
        finally:
            # Cleanup
            pygame.mixer.music.unload()
            if os.path.exists(filename):
                os.remove(filename)


class ProductService:
    """Handles product fetching and cart operations via API calls."""
    
    def __init__(self, base_url: str = BASE_URL, user_email: str = DEFAULT_USER_EMAIL):
        """Initialize product service."""
        self.base_url = base_url
        self.user_email = user_email
        self.products_cache = {}
        self.session = requests.Session()
        logger.info("Product service initialized")
    
    def fetch_products(self) -> Dict[str, Any]:
        """Fetch products from the database via API."""
        try:
            response = self.session.get(PRODUCTS_API_URL, timeout=10)
            response.raise_for_status()
            
            products_data = response.json()
            
            # Convert to the format expected by the shopping agent
            self.products_cache = {}
            for product in products_data:
                # Create search-friendly key from product name
                key = product['name'].lower().replace(' ', '').replace('-', '')
                self.products_cache[key] = {
                    "id": product['id'],
                    "name": product['name'],
                    "price": f"₹{product['price']}",
                    "description": product['description'],
                    "category": product.get('category', 'General'),
                    "imageUrl": product.get('imageUrl', '')
                }
            
            logger.info(f"Fetched {len(self.products_cache)} products from database")
            return self.products_cache
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch products: {e}")
            # Return fallback products if API fails
            return self._get_fallback_products()
        except Exception as e:
            logger.error(f"Unexpected error fetching products: {e}")
            return self._get_fallback_products()
    
    def _get_fallback_products(self) -> Dict[str, Any]:
        """Fallback products if API is unavailable."""
        return {
            "laptop": {"id": 1, "name": "Laptop", "price": "₹50,000", "description": "High-performance laptop", "category": "Electronics"},
            "smartphone": {"id": 2, "name": "Smartphone", "price": "₹25,000", "description": "Latest smartphone", "category": "Electronics"},
            "headphones": {"id": 3, "name": "Wireless Headphones", "price": "₹5,000", "description": "Premium audio quality", "category": "Audio"},
            "watch": {"id": 4, "name": "Smart Watch", "price": "₹15,000", "description": "Fitness and health tracking", "category": "Wearables"},
            "tablet": {"id": 5, "name": "Tablet", "price": "₹30,000", "description": "Perfect for work and entertainment", "category": "Electronics"}
        }
    
    def search_products(self, query: str) -> List[Dict[str, Any]]:
        """Search products by name, description, or category."""
        query = query.lower()
        matching_products = []
        
        for key, product in self.products_cache.items():
            if (query in product['name'].lower() or 
                query in product['description'].lower() or 
                query in product['category'].lower() or
                query in key):
                matching_products.append(product)
        
        return matching_products
    
    def get_product_by_name(self, name: str) -> Dict[str, Any]:
        """Get a specific product by name."""
        name_key = name.lower().replace(' ', '').replace('-', '')
        
        # Direct match
        if name_key in self.products_cache:
            return self.products_cache[name_key]
        
        # Fuzzy search
        for key, product in self.products_cache.items():
            if name.lower() in product['name'].lower() or key in name_key:
                return product
        
        return None
    
    def add_to_cart(self, product_id: int, quantity: int = 1) -> bool:
        """Add product to cart via API."""
        try:
            payload = {
                "productId": product_id,
                "email": self.user_email,
                "quantity": quantity
            }
            
            response = self.session.post(
                VOICE_CART_API_URL, 
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get('success'):
                logger.info(f"Successfully added product {product_id} to cart")
                return True
            else:
                logger.error(f"Failed to add to cart: {result.get('error', 'Unknown error')}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to add to cart: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error adding to cart: {e}")
            return False
    
    def get_products_summary(self) -> str:
        """Get a formatted summary of available products for AI prompts."""
        if not self.products_cache:
            self.fetch_products()
        
        summary = "Available products:\n"
        for product in self.products_cache.values():
            summary += f"- {product['name']} ({product['price']}) - {product['description']}\n"
        
        return summary


class ConversationMemory:
    """Manages conversation state and history."""
    
    def __init__(self):
        """Initialize conversation memory."""
        self.context = {"customer_info": {}, "order_info": {}}
        self.messages = []
        self.conversation_phase = "greeting"  # greeting, product_inquiry, details, checkout
        
    def add_user_message(self, message: str) -> None:
        """Add user message to conversation history."""
        self.messages.append({"role": "user", "content": message})
        
    def add_agent_message(self, message: str) -> None:
        """Add agent message to conversation history."""
        self.messages.append({"role": "agent", "content": message})
        
    def get_conversation_history(self, max_messages: int = 6) -> str:
        """Get formatted conversation history (limited to recent messages)."""
        # Get only the last N messages to keep prompts manageable
        recent_messages = self.messages[-max_messages:] if len(self.messages) > max_messages else self.messages
        
        history = ""
        for msg in recent_messages:
            prefix = "Customer" if msg["role"] == "user" else "Assistant"
            history += f"{prefix}: {msg['content']}\n"
        return history
    
    def set_context(self, key: str, data: Dict[str, Any]) -> None:
        """Set context information."""
        self.context[key] = data
        
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context information."""
        return self.context.get(key, default)


class ShoppingAgent:
    """AI agent for conducting shopping assistance in Hinglish using Gemini API."""
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        """Initialize the shopping agent."""
        self.memory = ConversationMemory()
        self.speech_handler = SpeechHandler()
        self.product_service = ProductService()
        self.running = False
        self.last_product_mentioned = None  # Track last mentioned product
        
        # Set up Gemini model
        self.model = genai.GenerativeModel(model_name)
        
        # Fetch products from database
        self.products = self.product_service.fetch_products()
        
        logger.info("Shopping agent initialized with database products")
        logger.info(f"Loaded {len(self.products)} products")
    
    def _get_prompt_template(self, phase: str) -> str:
        """Get the appropriate prompt template based on conversation phase."""
        
        # Get dynamic product list from database
        product_names = [p['name'] for p in self.products.values()]
        products_list = ", ".join(product_names)
        
        # Get products with prices for detailed view
        products_with_prices = []
        for product in self.products.values():
            products_with_prices.append(f"{product['name']} ({product['price']})")
        products_detailed = ", ".join(products_with_prices)
        
        templates = {
            "greeting": f"""
            You are a friendly shopping assistant speaking in Hinglish (mix of Hindi and English).
            
            Your goal is to help customers find and buy products.
            Available products: {products_list}
            
            Start with a warm greeting in Hinglish.
            Ask what they would like to buy today.
            Keep your response concise (2-3 sentences).
            """,
            
            "product_inquiry": f"""
            You are a friendly shopping assistant speaking in Hinglish (mix of Hindi and English).
            
            Available products: {products_detailed}
            
            Conversation history:
            {{conversation_history}}
            
            Customer's message: {{user_input}}
            
            Help the customer by:
            1. Understanding what they want to buy
            2. Providing product details and benefits
            3. Answering their questions
            4. Moving toward finalizing their choice
            
            Respond in Hinglish with enthusiasm.
            Keep your response concise (2-4 sentences).
            """,
            
            "details": """
            You are a friendly shopping assistant speaking in Hinglish (mix of Hindi and English).
            
            The customer has shown interest in a product. Now gather details like:
            - Quantity needed
            - Color preference (if applicable)
            - Any specific requirements
            - Confirm their choice
            
            Conversation history:
            {conversation_history}
            
            Customer's message: {user_input}
            
            Be helpful and move toward checkout.
            Respond in Hinglish.
            Keep your response concise (2-3 sentences).
            """,
            
            "checkout": """
            You are a friendly shopping assistant speaking in Hinglish (mix of Hindi and English).
            
            The customer is ready to buy. Complete the purchase by:
            1. Confirming their order
            2. Mentioning the total amount
            3. Ending with: "I have added to cart....Thank You!!!"
            
            Conversation history:
            {conversation_history}
            
            Customer's message: {user_input}
            
            Respond in Hinglish and conclude with the exact phrase "I have added to cart....Thank You!!!"
            Keep your response concise (2-3 sentences).
            """
        }
        
        return templates.get(phase, templates["product_inquiry"])
    
    def _format_prompt(self, template: str, user_input: str = "") -> str:
        """Format prompt template with context variables."""
        return template.format(
            conversation_history=self.memory.get_conversation_history(),
            user_input=user_input
        )
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using Gemini API."""
        logger.info("Generating response...")
        try:
            response = self.model.generate_content(prompt)
            result = response.text if hasattr(response, 'text') else str(response)
            return result
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return "Sorry, I'm having trouble right now. Kya aap phir se try kar sakte hain?"
    
    def _update_conversation_phase(self, user_input: str, agent_response: str) -> None:
        """Update conversation phase based on user input and agent response."""
        user_lower = user_input.lower()
        response_lower = agent_response.lower()
        
        logger.info(f"Current phase: {self.memory.conversation_phase}")
        
        # Check for checkout phrases and handle cart addition
        if "added to cart" in response_lower and "thank you" in response_lower:
            self._handle_checkout(user_input)
            self.memory.conversation_phase = "checkout"
            self.running = False  # End conversation after checkout
            logger.info("Conversation ending - checkout complete")
        # Check for confirmation words that indicate readiness to buy
        elif any(word in user_lower for word in ["yes", "haan", "ok", "okay", "sure", "buy", "order", "lena"]):
            if self.memory.conversation_phase == "greeting":
                self.memory.conversation_phase = "product_inquiry"
            elif self.memory.conversation_phase == "product_inquiry":
                self.memory.conversation_phase = "details"
            elif self.memory.conversation_phase == "details":
                self.memory.conversation_phase = "checkout"
        # Check if user is asking about specific products (dynamically from database)
        elif self._is_product_mentioned(user_lower):
            if self.memory.conversation_phase == "greeting":
                self.memory.conversation_phase = "product_inquiry"
        
        logger.info(f"Updated phase to: {self.memory.conversation_phase}")
    
    def _handle_checkout(self, user_input: str) -> None:
        """Handle the checkout process by adding items to cart."""
        product_to_buy = None
        
        # First try the last mentioned product
        if self.last_product_mentioned:
            product_to_buy = self.last_product_mentioned
        else:
            # Fallback: search conversation history
            conversation_text = self.memory.get_conversation_history().lower()
            
            for product in self.products.values():
                product_name_variants = [
                    product['name'].lower(),
                    product['name'].lower().replace(' ', ''),
                    product['name'].lower().split()[0] if ' ' in product['name'] else product['name'].lower()
                ]
                
                if any(variant in conversation_text for variant in product_name_variants):
                    product_to_buy = product
                    break
        
        if product_to_buy:
            success = self.product_service.add_to_cart(product_to_buy['id'])
            if success:
                logger.info(f"Added {product_to_buy['name']} to cart successfully")
                self.memory.set_context("last_purchase", product_to_buy)
            else:
                logger.error(f"Failed to add {product_to_buy['name']} to cart")
        else:
            logger.warning("Could not identify specific product for checkout")
    
    def _is_product_mentioned(self, user_input: str) -> bool:
        """Check if user mentioned any product from the database."""
        user_lower = user_input.lower()
        
        for product in self.products.values():
            # Check full product name
            if product['name'].lower() in user_lower:
                return True
            
            # Check individual words in product name
            product_words = product['name'].lower().split()
            for word in product_words:
                if len(word) > 2 and word in user_lower:  # Avoid checking very short words
                    return True
            
            # Check product name without spaces
            if product['name'].lower().replace(' ', '') in user_lower:
                return True
                
        return False

    def run_greeting_chain(self) -> str:
        """Generate greeting message to start the conversation."""
        template = self._get_prompt_template("greeting")
        prompt = self._format_prompt(template)
        
        result = self.generate_response(prompt)
        
        # Add to conversation history
        self.memory.add_agent_message(result)
        return result
    
    def run_conversation_chain(self, user_input: str) -> str:
        """Generate response to user input during the conversation."""
        # Add user input to memory
        self.memory.add_user_message(user_input)
        
        # Track mentioned products
        user_lower = user_input.lower()
        for product in self.products.values():
            if any(word in user_lower for word in [product['name'].lower(), product['name'].lower().replace(' ', '')]):
                self.last_product_mentioned = product
                break
        
        # Update conversation phase BEFORE generating response
        self._update_conversation_phase(user_input, "")
        
        # Get appropriate template based on current phase
        template = self._get_prompt_template(self.memory.conversation_phase)
        prompt = self._format_prompt(template, user_input)
        
        result = self.generate_response(prompt)
        
        # Add response to memory
        self.memory.add_agent_message(result)
        
        # Handle checkout if needed
        if "added to cart" in result.lower() and "thank you" in result.lower():
            self._handle_checkout(user_input)
            self.running = False
            logger.info("Conversation ending - checkout phrase detected")
        
        return result
    
    def start_shopping(self) -> None:
        """Start the shopping conversation."""
        self.running = True
        logger.info("Starting shopping session")
        
        try:
            # Greeting
            greeting = self.run_greeting_chain()
            self.speech_handler.speak(greeting)
            
            # Main conversation loop
            while self.running:
                user_input = self.speech_handler.recognize_speech()
                
                # Check for exit commands
                if user_input.lower() in ["bye", "goodbye", "end", "quit", "exit", "bye-bye"]:
                    break
                
                # Process non-empty input
                if user_input:
                    response = self.run_conversation_chain(user_input)
                    self.speech_handler.speak(response)
                    
                    # Check if checkout is complete
                    if "added to cart" in response.lower():
                        break
            
        except Exception as e:
            logger.error(f"Error during shopping: {e}")
            print(f"An error occurred: {e}")
        finally:
            self.end_shopping()
    
    def end_shopping(self) -> None:
        """End the shopping session."""
        self.running = False
        logger.info("Shopping session ended")
        print("Shopping session ended!")


def main():
    """Main function to run the shopping agent."""
    print("Hinglish Shopping Assistant")
    print("==========================")
    print("Ready to help you shop!")
    print("Say 'bye', 'goodbye', or 'end' to finish shopping.\n")
    
    agent = ShoppingAgent()
    agent.start_shopping()


if __name__ == "__main__":
    main()