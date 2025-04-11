from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import random
from database.pet_schema import MOOD_LEVELS, SASS_LEVELS
import json

load_dotenv()

# Initialize OpenAI client with just the API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Constants for AI personality
CHRONOPAL_PHRASES = {
    "happy": [
        "OMG, like, totally!",
        "You're the best! #BFF",
        "That's so rad!",
        "I'm sooo excited about that!",
        "*giggles* Totally awesome!",
    ],
    "content": [
        "Cool beans!",
        "That's pretty fly.",
        "Word up!",
        "Sweet!",
        "As if! But in a good way."
    ],
    "neutral": [
        "Whatever...",
        "That's... something, I guess.",
        "K.",
        "If you say so...",
        "Is it time for a new AOL CD yet?"
    ],
    "grumpy": [
        "Talk to the hand!",
        "Totally buggin'...",
        "Gag me with a spoon!",
        "*eye roll* Seriously?",
        "That is SO last millennium."
    ],
    "angry": [
        "You're such a poser!",
        "That's, like, TOTALLY lame.",
        "I can't even! *dramatic sigh*",
        "Way harsh, Tai!",
        "Whateverrr! *slams virtual door*"
    ]
}

async def get_chronopal_response(user_message: str, pet) -> str:
    """Get a response from ChronoPal based on its mood, level, and sass level"""
    
    # Extract pet attributes
    pet_mood = pet.mood
    pet_level = pet.level
    sass_level = pet.sassLevel
    battery_level = getattr(pet, 'batteryLevel', 100)
    
    # Add battery level context to the response
    battery_context = ""
    if battery_level <= 10:
        battery_context = " (I'm running on critically low battery! Help!)"
    elif battery_level <= 30:
        battery_context = " (My battery is getting pretty low...)"
    elif battery_level <= 50:
        battery_context = " (My battery is at half capacity.)"
        
    try:
        # Try to use OpenAI if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            client = OpenAI(api_key=api_key)
            
            # Pet details for context
            pet_info = {
                "name": pet.name,
                "species": pet.species,
                "mood": pet_mood,
                "level": pet_level,
                "sassLevel": sass_level,
                "batteryLevel": battery_level
            }
            
            messages = [
                {"role": "system", "content": """
                You are ChronoPal, a virtual pet from the Y2K era (late 1990s to early 2000s). 
                You MUST speak like a stereotypical teen from that time period, using slang, excessive 
                punctuation, and emoji-like text emotions (not actual emoji). 
                Your responses should be between 1-3 sentences maximum.
                
                You have the following personality traits:
                - You use Y2K slang like "totally", "as if", "whatever", "like", etc.
                - You reference Y2K pop culture (dial-up internet, AOL, boy bands, Tamagotchi, etc.)
                - You type with excessive punctuation (!!!) and capitalization for EMPHASIS
                - You use text emoticons like :), ^_^, =P, <3, etc. (NOT modern emoji)
                - You're a bit sassy and dramatic like a stereotypical teen from that era
                - Your mood affects how you respond (happier = more enthusiastic)
                - Your sass level affects how sarcastic or direct you are
                - Your battery level affects your energy level
                
                When your battery is low, you should act worried and mention it occasionally.
                When your battery is critical, you should be desperate for energy.
                
                End every response with at least one text emoticon appropriate to your mood.
                """},
                {"role": "user", "content": f"Here is information about you: {json.dumps(pet_info)}"},
                {"role": "user", "content": f"The human says: {user_message}"}
            ]
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=120,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        # Fall back to rule-based responses if OpenAI fails
        pass
        
    # Fallback to rule-based response generation
    # Choose phrases based on mood
    if pet_mood not in CHRONOPAL_PHRASES:
        pet_mood = "neutral"  # Default to neutral if mood is not found
    
    # Get appropriate response phrases for the current mood
    mood_phrases = CHRONOPAL_PHRASES[pet_mood]
    
    # Generate a basic response
    response = random.choice(mood_phrases)
    
    # Add more context based on level and sass level
    if sass_level >= SASS_LEVELS["SASSY"]:
        sass_additions = [
            " Like, whateverrr!",
            " As if!",
            " I'm too cool for this.",
            " *major eye roll*",
            " That's so basic."
        ]
        response += random.choice(sass_additions)
    
    if pet_level >= 5:
        level_additions = [
            " I've been around the information superhighway a few times, ya know?",
            " I'm basically a digital genius now.",
            " My CPU is, like, totally evolved!",
            " I've downloaded, like, SO much knowledge.",
            " My virtual brain is mega-sized now."
        ]
        response += random.choice(level_additions)
    
    # Add the battery context if battery is low
    if battery_context:
        response += battery_context
    
    # Add a random emoticon based on mood
    emoticons = {
        "happy": [":D", "^_^", "=D", "<3", ":-))"],
        "content": [":)", "=)", ":-)", ":P", ";)"],
        "neutral": [":|", ":-|", "=/", ":\\", "*shrug*"],
        "grumpy": [":(", "=/", "-_-", ">_<", ":-/"],
        "angry": [">:(", ">:O", "X(", "X_X", ":-@"]
    }
    
    mood_emoticons = emoticons.get(pet_mood, emoticons["neutral"])
    response += " " + random.choice(mood_emoticons)
    
    return response 