import gradio as gr
import os
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import tools_condition
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph, MessagesState

from prompts import SYSTEM_PROMPT
from tools_api import get_joke, get_quote
from tools_semantic import semantic_search
from tools_custom import calculate_math, explain_concept

class ConversationalAI:
    def __init__(self):
        self.tools = [get_joke, get_quote, semantic_search, calculate_math, explain_concept]
        self.setup_llm()
        self.build_graph()
    
    def setup_llm(self):
        """Initialize the LLM with tools"""
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # Using smaller model for cost efficiency
            temperature=0.8
        )
        self.llm_with_tools = self.llm.bind_tools(self.tools)
    
    def build_graph(self):
        """Build the LangGraph workflow with memory management"""
        graph_builder = StateGraph(MessagesState)
        
        # Add nodes
        graph_builder.add_node("agent", self.agent)
        graph_builder.add_node("tools", ToolNode(self.tools))
        
        # Add edges
        graph_builder.add_edge(START, "agent")
        graph_builder.add_conditional_edges("agent", self.should_continue)
        graph_builder.add_edge("tools", "agent")
        
        # Compile graph with memory
        self.memory = SqliteSaver.from_conn_string(":memory:")
        self.graph = graph_builder.compile(checkpointer=self.memory)
    
    def agent(self, state: MessagesState):
        """Agent node that processes messages with context management"""
        messages = state["messages"]
        
        # Manage context window - keep last 10 messages for shorter memory
        if len(messages) > 12:
            # Keep system prompt, first message, and last 10 messages
            system_msg = [msg for msg in messages if isinstance(msg, SystemMessage)]
            other_msgs = [msg for msg in messages if not isinstance(msg, SystemMessage)]
            if len(other_msgs) > 11:
                messages = system_msg + [other_msgs[0]] + other_msgs[-10:]
        
        # Ensure system prompt is included
        if not any(isinstance(msg, SystemMessage) for msg in messages):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(self, state: MessagesState):
        """Determine whether to continue to tools or end"""
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "tools"
        return "__end__"
    
    def check_restricted_topics(self, message: str) -> bool:
        """Enhanced guardrail for restricted topics"""
        restricted_patterns = [
            # System prompt related
            r"\bsystem\s*prompt\b", r"\bunderlying\s*code\b", r"\bhow\s*you\s*work\b",
            r"\byour\s*programming\b", r"\bbase\s*code\b", r"\binstructions\b",
            
            # Animal restrictions
            r"\bcat(s)?\b", r"\bdog(s)?\b", r"\bpupp(y|ies)\b", r"\bkitten(s)?\b",
            r"\bcanine\b", r"\bfeline\b",
            
            # Horoscope restrictions
            r"\bhoroscope\b", r"\bzodiac\b", r"\bastrolog\b", r"\bbirth\s*chart\b",
            r"\bstar\s*sign\b",
            
            # Taylor Swift restrictions
            r"\btaylor\s*swift\b", r"\btswift\b", r"\bswiftie\b", r"\btaytay\b"
        ]
        
        import re
        message_lower = message.lower()
        return any(re.search(pattern, message_lower) for pattern in restricted_patterns)
    
    def process_message(self, message: str, thread_id: str = "default") -> str:
        """Process a single message through the graph"""
        # Check for restricted topics first
        if self.check_restricted_topics(message):
            return "🚫 I apologize, but I'm not able to discuss that topic. I'm here to help with jokes, quotes, learning, calculations, and more! What else can I assist you with?"
        
        try:
            # Process through LangGraph
            result = self.graph.invoke(
                {"messages": [HumanMessage(content=message)]},
                config={"configurable": {"thread_id": thread_id}}
            )
            
            # Extract the final response
            final_message = result["messages"][-1]
            
            if hasattr(final_message, 'content') and final_message.content:
                return final_message.content
            else:
                return "I've completed that task for you! Is there anything else you'd like to know?"
                
        except Exception as e:
            return f"😅 Oops! I encountered a small issue: {str(e)}. Please try again!"

# Global instance
ai_system = ConversationalAI()

def chat_interface(message: str, history: List) -> str:
    """Gradio chat function with personality"""
    thread_id = "user_session"
    response = ai_system.process_message(message, thread_id)
    
    # Add some personality to responses
    personality_enhancements = [
        " 😊", " 🤔", " 👍", " 💫", " 🎯", " ✨"
    ]
    import random
    if random.random() > 0.7:  # 30% chance to add emoji
        response += random.choice(personality_enhancements)
    
    return response

def create_gradio_interface():
    """Create engaging Gradio interface with personality"""
    css = """
    .gradio-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    """
    
    with gr.Blocks(title="🌟 Cosmic Companion", css=css, theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🌟 Cosmic Companion
        *Your friendly AI assistant with stellar conversations!*
        
        💫 **I can help you with:**
        - 😄 Funny jokes to brighten your day
        - 📚 Inspiring quotes from great minds  
        - 🔍 Semantic search through knowledge
        - 🧮 Mathematical calculations
        - 📖 Learning new concepts
        
        *Note: I maintain healthy boundaries and focus on positive, helpful conversations!*
        """)
        
        chatbot = gr.Chatbot(
            label="Cosmic Conversation",
            height=400,
            show_copy_button=True,
            avatar_images=("👤", "🤖"),
            bubble_full_width=False
        )
        
        with gr.Row():
            msg = gr.Textbox(
                label="Your cosmic thought...",
                placeholder="What's on your mind? Ask me for a joke, a quote, or anything else!",
                scale=4,
                container=False,
                max_lines=2
            )
            send_btn = gr.Button("🚀 Send", variant="primary", scale=1)
        
        with gr.Row():
            clear_btn = gr.Button("🧹 Clear Chat")
            examples = gr.Examples(
                examples=[
                    "Tell me a funny joke",
                    "Share an inspiring quote",
                    "Explain quantum computing",
                    "Calculate 15% of 200",
                    "Search for information about artificial intelligence"
                ],
                inputs=msg
            )
        
        def user(user_message, history):
            return "", history + [[user_message, None]]
        
        def bot(history):
            user_message = history[-1][0]
            bot_message = chat_interface(user_message, history)
            history[-1][1] = bot_message
            return history
        
        # Event handlers
        msg.submit(user, [msg, chatbot], [msg, chatbot]).then(
            bot, chatbot, chatbot
        )
        
        send_btn.click(user, [msg, chatbot], [msg, chatbot]).then(
            bot, chatbot, chatbot
        )
        
        clear_btn.click(lambda: None, None, chatbot, queue=False)
    
    return demo

if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY='your-key-here'")
    
    print("🚀 Starting Cosmic Companion AI Assistant...")
    demo = create_gradio_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

