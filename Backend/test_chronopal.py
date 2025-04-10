from api.ai_personality import get_chronopal_response

def test_chronopal():
    # Test different moods, levels, and sass levels
    test_cases = [
        # Basic interactions
        ("hello", "happy", 1, 1),
        ("how are you?", "excited", 3, 2),
        ("what's your favorite food?", "default", 2, 3),
        
        # Advice requests
        ("give me some life advice", "happy", 4, 2),
        ("what should I do about my messy room?", "default", 1, 1),
        ("I'm feeling stressed, any tips?", "excited", 3, 4),
        
        # Tech advice requests
        ("how do I fix my slow computer?", "happy", 2, 3),
        ("what's the best way to backup my files?", "default", 5, 2),
        ("should I upgrade to Windows 11?", "excited", 1, 5),
        ("what's your opinion on social media?", "happy", 3, 4),
        
        # Mixed interactions
        ("tell me a joke", "happy", 5, 1),
        ("are you hungry?", "default", 1, 3),
        ("what's your favorite game?", "happy", 3, 2),
        ("do you like music?", "excited", 2, 5),
    ]

    print("🤖 Testing ChronoPal's AI Personality 🤖")
    print("=" * 50)
    
    for message, mood, level, sass_level in test_cases:
        print(f"\nUser: {message}")
        print(f"Pet Mood: {mood}, Level: {level}, Sass Level: {sass_level}")
        response = get_chronopal_response(message, mood, level, sass_level)
        print(f"ChronoPal: {response}")
        print("-" * 50)

if __name__ == "__main__":
    test_chronopal() 