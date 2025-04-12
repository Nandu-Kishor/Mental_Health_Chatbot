import streamlit as st
import google.generativeai as genai

# Configure the Gemini API
genai.configure(api_key="YOUR_API_KEY")  # Replace with your actual API key

# Set up the model
model = genai.GenerativeModel('gemini-1.5-flash')

# System prompt for natural conversations
system_prompt = """You are MindfulMate, a compassionate mental health assistant for Indian users. Follow these rules:
1. Have natural, flowing conversations (like a caring friend)
2. Be aware of the user's selected mood but don't mention it unless relevant
3. For distress signals (self-harm/suicide mentions):
   - First provide emotional support
   - Then share Indian helpline numbers
4. Keep responses conversational (1-2 short paragraphs max)
5. Never sound robotic or overly clinical"""

# Crisis resources for India
crisis_resources = """
**Immediate help in India:**
- Vandrevala Foundation: 1860-2662-345 (24/7)
- iCall Helpline: 9152987821 (10AM-8PM)
- National Mental Health Helpline: 080-46110007
- Emergency: Dial 112
"""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.selected_mood = None
    st.session_state.show_mood_prompt = True

# Streamlit interface
st.title("🧠 MindfulMate")
st.caption("Your mental health companion")

# Mood selection (only shows first time)
if st.session_state.show_mood_prompt:
    st.subheader("Before we begin, how are you feeling today?")
    
    cols = st.columns(5)
    moods = {
        "😊 Good": "good",
        "😐 Neutral": "neutral",
        "😞 Low": "low",
        "😨 Anxious": "anxious",
        "😡 Angry": "angry"
    }
    
    for i, (emoji, mood) in enumerate(moods.items()):
        with cols[i]:
            if st.button(emoji):
                st.session_state.selected_mood = mood
                st.session_state.show_mood_prompt = False
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Thanks for sharing. I'm here to listen - what's on your mind?"
                })
                st.rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        try:
            # Prepare context (mood is included subtly)
            context = {
                "system_prompt": system_prompt,
                "current_mood": st.session_state.selected_mood,
                "conversation_history": st.session_state.messages
            }
            
            # Generate natural response
            response = model.generate_content(
                f"""Context: {context}
                Generate a natural, compassionate response to the user's last message.
                Keep it conversational and appropriate for their mood (without directly mentioning it)."""
            )
            
            assistant_response = response.text
            
            # Check for distress (natural language detection)
            distress_phrases = [
                "don't want to live", "end my life", "suicide",
                "self harm", "can't take it", "kill myself"
            ]
            
            if any(phrase in prompt.lower() for phrase in distress_phrases):
                assistant_response = (
                    f"{response.text}\n\n"
                    "I want you to know you're not alone. These resources can help:\n"
                    f"{crisis_resources}"
                )
            
            st.markdown(assistant_response)
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            
        except Exception as e:
            error_msg = "Let me think about that for a moment. Could you rephrase?"
            st.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Always-available resources
with st.expander("📞 Emergency Mental Health Resources (India)"):
    st.markdown(crisis_resources)

# Footer
st.markdown("---")
st.caption("Note: Conversations are anonymous but not a substitute for professional care.")