import streamlit as st
from groq import Groq

# Groq API Client
client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

# Store the model
if "llm" not in st.session_state:
    st.session_state["llm"] = ""


# Store the chat messages
if "messages" not in st.session_state:
    st.session_state["messages"] = []

print("Session State: ", st.session_state)

# Page Header
st.header("Chatbot Playground", divider="orange", anchor=False)
st.title(":orange[Chat App]", anchor=False)
st.subheader("Powered by Groq")


# Sidebar
st.sidebar.title("Parameters")

# Model Selection
def reset_chat():
    st.session_state.messages = []
    st.toast(f"Model Selected: {st.session_state.llm}", icon="🤖")

st.session_state.llm = st.sidebar.selectbox("Select Model", [
    "llama3-8b-8192", "mixtral-8x7b-32768", "gemma2-9b-it"
], index=0, on_change=reset_chat)


# Parameters
temp = st.sidebar.slider("Temperature", 0.0, 2.0, value=1.0)
max_tokens = st.sidebar.slider("Max Tokens", 0, 8192, value=1024)
stream = st.sidebar.toggle("Stream", value=True)
json_mode = st.sidebar.toggle("JSON Mode", help="You must also ask the model to return JSON.")

# Advanced Parameters
with st.sidebar.expander("Advanced"):
    top_p = st.slider("Top P", 0.0, 1.0, help="It's not recommended to alter both the temperature and the top-p.")
    stop_seq = st.text_input("Stop Sequence")
    
    
# Show the chat messages
for message in st.session_state.messages:
    # {"role": "user", "content": "hello world"}
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        
# Show input for the user prompt
if prompt := st.chat_input():
    # add the message/prompt to the messages list
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )
    
    # show the new user message
    with st.chat_message("user"):
        st.write(prompt)
        
        
    # Make API call and show the model response
    with st.chat_message("assistant"):
        # create empty container for response
        response_text = st.empty()
        
        # Make the API call to Groq
        completion = client.chat.completions.create(
            model=st.session_state.llm or "llama3-8b-8192",
            messages=st.session_state.messages,
            stream=stream,
            temperature=temp,
            max_tokens=max_tokens,
            response_format= {"type": "json_object"} if json_mode else {"type": "text"},
            stop=stop_seq,
            top_p=top_p
        )
        
        # Display the full message
        full_response = ""
        
        if stream:
            for chunk in completion:
                full_response += chunk.choices[0].delta.content or ""
                response_text.write(full_response)
        else:
            with st.spinner("Generating"):
                completion.choices[0].message.content
            
        # Add assistant message to the messages list
        st.session_state.messages.append({"role": "assistant", "content": full_response})