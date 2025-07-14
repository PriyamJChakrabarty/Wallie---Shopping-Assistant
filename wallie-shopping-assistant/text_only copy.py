import os
import re
import time
import json
import uuid
import logging
from typing import Dict, List, Any

import requests

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
    GEMINI_API_KEY = 'YOUR_API_KEY'  # Replace with actual key
    BASE_URL = "http://localhost:3000"
    DEFAULT_USER_EMAIL = "voice-assistant@example.com"

genai.configure(api_key=GEMINI_API_KEY)

# Configuration for Next.js application
PRODUCTS_API_URL = f"{BASE_URL}/api/products"
VOICE_CART_API_URL = f"{BASE_URL}/api/voice-cart"


class ProductService:
    """Handles product fetching and cart operations via API calls."""
    def __init__(self, base_url: str = BASE_URL, user_email: str = DEFAULT_USER_EMAIL):
        self.base_url = base_url
        self.user_email = user_email
        self.products_cache = {}
        self.session = requests.Session()
        logger.info("Product service initialized")

    def fetch_products(self) -> Dict[str, Any]:
        try:
            response = self.session.get(PRODUCTS_API_URL, timeout=10)
            response.raise_for_status()
            products_data = response.json()
            self.products_cache = {}

            for product in products_data:
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
            return self._get_fallback_products()
        except Exception as e:
            logger.error(f"Unexpected error fetching products: {e}")
            return self._get_fallback_products()

    def _get_fallback_products(self) -> Dict[str, Any]:
        return {
            "laptop": {"id": 1, "name": "Laptop", "price": "₹50,000", "description": "High-performance laptop", "category": "Electronics"},
            "smartphone": {"id": 2, "name": "Smartphone", "price": "₹25,000", "description": "Latest smartphone", "category": "Electronics"},
            "headphones": {"id": 3, "name": "Wireless Headphones", "price": "₹5,000", "description": "Premium audio quality", "category": "Audio"},
            "watch": {"id": 4, "name": "Smart Watch", "price": "₹15,000", "description": "Fitness and health tracking", "category": "Wearables"},
            "tablet": {"id": 5, "name": "Tablet", "price": "₹30,000", "description": "Perfect for work and entertainment", "category": "Electronics"}
        }

    def search_products(self, query: str) -> List[Dict[str, Any]]:
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
        name_key = name.lower().replace(' ', '').replace('-', '')
        if name_key in self.products_cache:
            return self.products_cache[name_key]
        for key, product in self.products_cache.items():
            if name.lower() in product['name'].lower() or key in name_key:
                return product
        return None

    def add_to_cart(self, product_id: int, quantity: int = 1) -> bool:
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


class ConversationMemory:
    def __init__(self):
        self.context = {"customer_info": {}, "order_info": {}}
        self.messages = []
        self.conversation_phase = "greeting"

    def add_user_message(self, message: str) -> None:
        self.messages.append({"role": "user", "content": message})

    def add_agent_message(self, message: str) -> None:
        self.messages.append({"role": "agent", "content": message})

    def get_conversation_history(self, max_messages: int = 6) -> str:
        recent_messages = self.messages[-max_messages:] if len(self.messages) > max_messages else self.messages
        history = ""
        for msg in recent_messages:
            prefix = "Customer" if msg["role"] == "user" else "Assistant"
            history += f"{prefix}: {msg['content']}\n"
        return history

    def set_context(self, key: str, data: Dict[str, Any]) -> None:
        self.context[key] = data

    def get_context(self, key: str, default: Any = None) -> Any:
        return self.context.get(key, default)


class ShoppingAgent:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.memory = ConversationMemory()
        self.product_service = ProductService()
        self.running = False
        self.last_product_mentioned = None
        self.model = genai.GenerativeModel(model_name)
        self.products = self.product_service.fetch_products()
        logger.info("Shopping agent initialized with database products")
        logger.info(f"Loaded {len(self.products)} products")

    def _get_prompt_template(self, phase: str) -> str:
        product_names = [p['name'] for p in self.products.values()]
        products_list = ", ".join(product_names)
        products_with_prices = [f"{p['name']} ({p['price']})" for p in self.products.values()]
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
        return template.format(
            conversation_history=self.memory.get_conversation_history(),
            user_input=user_input
        )

    def generate_response(self, prompt: str) -> str:
        logger.info("Generating response...")
        try:
            response = self.model.generate_content(prompt)
            result = response.text if hasattr(response, 'text') else str(response)
            return result
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return "Sorry, I'm having trouble right now. Kya aap phir se try kar sakte hain?"

    def _update_conversation_phase(self, user_input: str, agent_response: str) -> None:
        user_lower = user_input.lower()
        response_lower = agent_response.lower()
        logger.info(f"Current phase: {self.memory.conversation_phase}")

        if "added to cart" in response_lower and "thank you" in response_lower:
            self._handle_checkout(user_input)
            self.memory.conversation_phase = "checkout"
            self.running = False
        elif any(word in user_lower for word in ["yes", "haan", "ok", "okay", "sure", "buy", "order", "lena"]):
            if self.memory.conversation_phase == "greeting":
                self.memory.conversation_phase = "product_inquiry"
            elif self.memory.conversation_phase == "product_inquiry":
                self.memory.conversation_phase = "details"
            elif self.memory.conversation_phase == "details":
                self.memory.conversation_phase = "checkout"
        elif self._is_product_mentioned(user_lower):
            if self.memory.conversation_phase == "greeting":
                self.memory.conversation_phase = "product_inquiry"

        logger.info(f"Updated phase to: {self.memory.conversation_phase}")

    def _handle_checkout(self, user_input: str) -> None:
        product_to_buy = self.last_product_mentioned
        if not product_to_buy:
            conversation_text = self.memory.get_conversation_history().lower()
            for product in self.products.values():
                variants = [
                    product['name'].lower(),
                    product['name'].lower().replace(' ', ''),
                    product['name'].split()[0].lower()
                ]
                if any(v in conversation_text for v in variants):
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
        user_lower = user_input.lower()
        for product in self.products.values():
            if product['name'].lower() in user_lower:
                return True
            product_words = product['name'].lower().split()
            for word in product_words:
                if len(word) > 2 and word in user_lower:
                    return True
            if product['name'].lower().replace(' ', '') in user_lower:
                return True
        return False

    def run_greeting_chain(self) -> str:
        template = self._get_prompt_template("greeting")
        prompt = self._format_prompt(template)
        result = self.generate_response(prompt)
        self.memory.add_agent_message(result)
        return result

    def run_conversation_chain(self, user_input: str) -> str:
        self.memory.add_user_message(user_input)
        user_lower = user_input.lower()
        for product in self.products.values():
            if any(word in user_lower for word in [product['name'].lower(), product['name'].lower().replace(' ', '')]):
                self.last_product_mentioned = product
                break

        self._update_conversation_phase(user_input, "")
        template = self._get_prompt_template(self.memory.conversation_phase)
        prompt = self._format_prompt(template, user_input)
        result = self.generate_response(prompt)
        self.memory.add_agent_message(result)

        if "added to cart" in result.lower() and "thank you" in result.lower():
            self._handle_checkout(user_input)
            self.running = False
            logger.info("Conversation ending - checkout phrase detected")

        return result
