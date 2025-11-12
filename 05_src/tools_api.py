from langchain_core.tools import tool
import requests
import json

@tool
def get_joke() -> str:
    """Get a random joke from a public API and deliver it in a fun, engaging way."""
    try:
        # Using JokeAPI - a free joke API
        response = requests.get("https://v2.jokeapi.dev/joke/Any?type=twopart&safe-mode")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('error', False):
                return "😅 The joke service seems to be taking a coffee break! Why don't you try asking me something else?"
            
            if data['type'] == 'twopart':
                setup = data['setup']
                delivery = data['delivery']
                # Rephrase and add personality
                return f"🎭 Here's a joke for you!\n\n**{setup}**\n\n...wait for it...\n\n**{delivery}** 😄"
            else:
                joke = data.get('joke', 'Why was the computer cold? It left its Windows open!')
                return f"😂 Get ready to smile!\n\n\"{joke}\"\n\nHope that brightened your day! ✨"
        else:
            return "📡 Hmm, the joke lines are busy right now. But here's one I know: Why do programmers prefer dark mode? Because light attracts bugs! 🐛"
            
    except Exception as e:
        return "😊 While I work on connecting to the joke service, remember: Laughter is the best medicine! What else can I help you with today?"

@tool
def get_quote() -> str:
    """Get an inspiring quote from an API and present it meaningfully."""
    try:
        # Using ZenQuotes API - free quotes API
        response = requests.get("https://zenquotes.io/api/random")
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                quote = data[0]['q']
                author = data[0]['a']
                
                # Transform and rephrase the output
                inspirational_intros = [
                    "🌟 Here's some wisdom to brighten your day:",
                    "📚 I came across this beautiful thought:",
                    "💫 Let this quote inspire you:",
                    "🎯 Some timeless wisdom for you:",
                    "✨ A powerful reminder:"
                ]
                
                import random
                intro = random.choice(inspirical_intros)
                
                return f"{intro}\n\n\"{quote}\"\n\n— {author}\n\nLet that sink in... 💭"
            else:
                return "📖 \"The only way to do great work is to love what you do.\" — Steve Jobs\n\nRemember to follow your passion! 💫"
        else:
            return "💡 \"The future belongs to those who believe in the beauty of their dreams.\" — Eleanor Roosevelt\n\nKeep dreaming big! 🚀"
            
    except Exception as e:
        return "🌱 \"The journey of a thousand miles begins with a single step.\" — Lao Tzu\n\nEvery great achievement starts with taking that first step! 👍"
