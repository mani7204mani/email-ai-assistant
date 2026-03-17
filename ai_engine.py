from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)

summary_prompt = PromptTemplate(
    input_variables=["email_body", "sender", "subject"],
    template="""
    You are an intelligent email assistant.
    
    Sender: {sender}
    Subject: {subject}
    Email: {email_body}
    
    Provide:
    1. A 2-3 sentence summary
    2. The priority level (High / Medium / Low)
    3. Key action items (if any)
    
    Be concise and professional.
    """
)

reply_prompt = PromptTemplate(
    input_variables=["email_body", "sender", "subject"],
    template="""
    You are a professional email assistant.
    
    Sender: {sender}
    Subject: {subject}
    Email: {email_body}
    
    Write 2 different reply options:
    Option 1: A brief, direct reply (2-3 sentences)
    Option 2: A detailed, formal reply (1 paragraph)
    
    Label them clearly as "Option 1:" and "Option 2:"
    """
)

summary_chain = summary_prompt | llm
reply_chain   = reply_prompt | llm

def summarize_email(email):
    result = summary_chain.invoke({
        "email_body": email['body'],
        "sender":     email['sender'],
        "subject":    email['subject']
    })
    return result.content

def generate_replies(email):
    result = reply_chain.invoke({
        "email_body": email['body'],
        "sender":     email['sender'],
        "subject":    email['subject']
    })
    return result.content