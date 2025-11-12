from langchain_core.tools import tool
import math

@tool
def calculate_math(expression: str) -> str:
    """Perform mathematical calculations and explain the process in an educational way."""
    
    # Safe evaluation with basic operations
    allowed_operations = {
        'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
        'sqrt': math.sqrt, 'log': math.log, 'log10': math.log10,
        'exp': math.exp, 'pi': math.pi, 'e': math.e,
        'pow': pow, 'abs': abs, 'round': round
    }
    
    # Security check
    dangerous_keywords = ['import', 'exec', 'eval', '__', 'open', 'file']
    if any(keyword in expression.lower() for keyword in dangerous_keywords):
        return "🚫 I can't calculate that expression for security reasons. Please try a basic mathematical operation."
    
    try:
        # Evaluate safely
        result = eval(expression, {"__builtins__": {}}, allowed_operations)
        
        # Create educational explanation
        explanations = {
            '+': 'adding',
            '-': 'subtracting', 
            '*': 'multiplying',
            '/': 'dividing',
            '**': 'raising to the power of',
            'sqrt': 'taking the square root of'
        }
        
        # Simple explanation based on operators
        explanation = ""
        for op, desc in explanations.items():
            if op in expression:
                explanation = f" I'm {desc} the numbers."
                break
        
        return f"🧮 **Calculation Result:**\n`{expression} = {result}`\n\n{explanation}✨ *Math is amazing!*"
        
    except Exception as e:
        return f"❌ I couldn't calculate `{expression}`. Make sure it's a valid mathematical expression like '2 + 2', 'sqrt(16)', or 'sin(90)'."

@tool
def explain_concept(topic: str) -> str:
    """Explain complex concepts in simple, easy-to-understand terms with examples."""
    
    # Pre-defined explanations for common topics
    concept_explanations = {
        "artificial intelligence": "🤖 **Artificial Intelligence (AI)** is like teaching computers to think and learn like humans! It's the science of creating smart machines that can solve problems, recognize patterns, and make decisions.\n\n*Example:* When Netflix recommends shows you might like, that's AI learning your preferences!",
        
        "machine learning": "📊 **Machine Learning** is a type of AI where computers learn from data without being explicitly programmed for every task. It's like showing examples to a child until they learn the pattern!\n\n*Example:* Spam filters learn what spam looks like by analyzing thousands of emails.",
        
        "quantum computing": "⚛️ **Quantum Computing** uses the strange rules of quantum physics to solve problems too complex for regular computers. Instead of regular bits (0 or 1), it uses qubits that can be both 0 and 1 at the same time!\n\n*Think of it like:* Being able to read every book in a library simultaneously instead of one by one.",
        
        "blockchain": "⛓️ **Blockchain** is a digital ledger that records transactions across many computers, making it secure and hard to tamper with. Each 'block' contains transactions, and they're 'chained' together.\n\n*Simple analogy:* Like a shared Google Doc that everyone can see but no one can edit without others knowing.",
        
        "climate change": "🌍 **Climate Change** refers to long-term changes in Earth's weather patterns, mainly caused by human activities like burning fossil fuels. It's like Earth having a fever because of too many greenhouse gases trapping heat.\n\n*Impact:* Rising sea levels, extreme weather, and ecosystem changes."
    }
    
    topic_lower = topic.lower()
    
    for key, explanation in concept_explanations.items():
        if key in topic_lower:
            return explanation
    
    # For unknown topics, provide a general response
    return f"📖 I'd be happy to explain **{topic}**! While I prepare a detailed explanation, here's what I understand:\n\n{topic.title()} is an important concept that involves various interesting aspects. It's a fascinating topic worth exploring! 💫\n\n*Want me to search my knowledge base for more specific information about {topic}?*"