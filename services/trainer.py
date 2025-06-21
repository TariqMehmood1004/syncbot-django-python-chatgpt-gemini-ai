import pandas as pd
from EmergibotApp.models import ChatSession, ChatMessage
from EmergibotApp.utils import chatbot_fallback_response, generate_response_variations
from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
import random
import os
from django.conf import settings


# Initialize the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)  # Add this to your Django settings
gemini_model = genai.GenerativeModel('gemini-2.5-flash')

def preprocess_data():
    """
    Load and process data from the Excel sheet for the knowledge base.
    """
    file_path = 'data/mentee_mentor_questions.xlsx'
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found.")

    excel_data = pd.read_excel(file_path)
    knowledge_base = []

    for _, row in excel_data.iterrows():
        if 'Questions' in excel_data.columns and 'Answers' in excel_data.columns:
            question = str(row['Questions']).strip()
            answer = str(row['Answers']).strip()

            if question and answer:
                question_embedding = model.encode(question, convert_to_tensor=True)
                knowledge_base.append({
                    "question": question,
                    "answer": answer,
                    "embedding": question_embedding
                })

    return knowledge_base

knowledge_base = preprocess_data()

def search_knowledge_base(user_input, threshold=0.8):
    """
    Search the knowledge base using semantic similarity for the most accurate match.
    """
    user_embedding = model.encode(user_input, convert_to_tensor=True)
    best_match = None
    highest_score = 0

    for entry in knowledge_base:
        score = util.cos_sim(user_embedding, entry["embedding"]).item()
        if score > highest_score:
            highest_score = score
            best_match = entry

    return (best_match, highest_score) if highest_score >= threshold else (None, highest_score)

def get_gemini_response(user_input, context=""):
    """
    Generate response using Google Gemini AI.
    """
    try:
        # Create a context-aware prompt
        prompt = f"""
        You are a helpful mentorship chatbot. Please provide a supportive and informative response to the following question.
        
        Context: {context}
        User Question: {user_input}
        
        Please provide a helpful, encouraging, and professional response suitable for a mentee-mentor conversation.
        """
        
        response = gemini_model.generate_content(prompt)
        print(f"Gemini response: {response.text.strip()}")
        if not response or not response.text.strip():
            raise ValueError("Gemini response is empty or invalid.")
        
        return response.text.strip()
    except Exception as e:
        print(f"Error generating Gemini response: {e}")
        return None

def update_excel(user_input, bot_response, response_source="knowledge_base"):
    """
    Update the Excel file with user input and bot response for future reference.
    """
    file_path = 'data/updated_records.xlsx'
    df = pd.read_excel(file_path) if os.path.exists(file_path) else pd.DataFrame(columns=["Questions", "Answers", "Source"])

    new_record = pd.DataFrame([{
        "Questions": user_input, 
        "Answers": bot_response,
        "Source": response_source
    }])
    updated_df = pd.concat([df, new_record], ignore_index=True)
    updated_df.to_excel(file_path, index=False)
    print(f"Updated Excel file: {file_path}")

def classify_sentence_type(sentence):
    """
    Classify the sentence type as declarative, interrogative, imperative, or exclamatory.
    """
    sentence = sentence.strip()
    if sentence.endswith('?'):
        return "interrogative"
    elif sentence.endswith('!'):
        return "exclamatory"
    elif sentence.split()[0].lower() in ['please', 'do', 'let', 'kindly']:
        return "imperative"
    else:
        return "declarative"

def categorize_response(answer):
    """
    Categorize the answer as 'yes', 'no', or 'other relevant context'.
    """
    answer_lower = answer.lower()
    if any(phrase in answer_lower for phrase in ['yes', 'of course', 'sure', 'absolutely']):
        return "yes"
    elif any(phrase in answer_lower for phrase in ['no', 'not', 'cannot', "don't"]):
        return "no"
    else:
        return "other relevant context"

def get_response(user_input, ip_address, use_gemini=True, similarity_threshold=0.7):
    """
    Generate a dynamic and categorized response using either knowledge base or Gemini AI.
    
    Args:
        user_input: The user's question or message
        ip_address: IP address for session tracking
        use_gemini: Whether to use Gemini for fallback responses
        similarity_threshold: Threshold for knowledge base matching
    """
    session, _ = ChatSession.objects.get_or_create(ip_address=ip_address)
    match, score = search_knowledge_base(user_input, threshold=similarity_threshold)
    
    response_source = "knowledge_base"
    bot_response = None

    if match:
        # Use knowledge base response with variations
        core_answer = match["answer"]
        bot_response = random.choice(generate_response_variations(core_answer))
        response_source = "knowledge_base"
        print(f"Knowledge base match found with score: {score:.3f}")
    else:
        # Try Gemini AI if no good match in knowledge base
        if use_gemini:
            print(f"No knowledge base match (score: {score:.3f}), trying Gemini...")
            gemini_response = get_gemini_response(user_input)
            
            if gemini_response:
                bot_response = gemini_response
                response_source = "gemini"
                print("Gemini response generated successfully")
            else:
                # Final fallback
                bot_response = chatbot_fallback_response()
                response_source = "fallback"
                print("Using fallback response")
        else:
            # Use fallback response if Gemini is disabled
            bot_response = chatbot_fallback_response()
            response_source = "fallback"
            print("Using fallback response (Gemini disabled)")

    # Log the response in the Excel file with source information
    update_excel(user_input, bot_response, response_source)

    # Save the chat message in the database
    ChatMessage.objects.create(
        session=session,
        user_message=user_input,
        bot_response=bot_response
    )

    # Classify sentence type and categorize the response
    sentence_type = classify_sentence_type(bot_response)
    response_category = categorize_response(bot_response)

    return {
        "response": bot_response,
        "sentence_type": sentence_type,
        "response_category": response_category,
        "response_source": response_source,
        "similarity_score": score if match else 0
    }

def get_conversation_context(session, max_messages=3):
    """
    Get recent conversation context for better Gemini responses.
    """
    recent_messages = ChatMessage.objects.filter(
        session=session
    ).order_by('-created_at')[:max_messages]
    
    context = []
    for msg in reversed(recent_messages):
        context.append(f"User: {msg.user_message}")
        context.append(f"Bot: {msg.bot_response}")
    
    return "\n".join(context)

def get_contextual_response(user_input, ip_address, use_context=True):
    """
    Enhanced response function that includes conversation context for Gemini.
    """
    session, _ = ChatSession.objects.get_or_create(ip_address=ip_address)
    
    # Get conversation context if enabled
    context = ""
    if use_context:
        context = get_conversation_context(session)
    
    match, score = search_knowledge_base(user_input, threshold=0.7)
    response_source = "knowledge_base"
    bot_response = None

    if match:
        # Use knowledge base response
        core_answer = match["answer"]
        bot_response = random.choice(generate_response_variations(core_answer))
        response_source = "knowledge_base"
    else:
        # Use Gemini with context
        gemini_response = get_gemini_response(user_input, context)
        
        if gemini_response:
            bot_response = gemini_response
            response_source = "gemini"
        else:
            bot_response = chatbot_fallback_response()
            response_source = "fallback"

    # Log and save response
    update_excel(user_input, bot_response, response_source)
    
    ChatMessage.objects.create(
        session=session,
        user_message=user_input,
        bot_response=bot_response
    )

    # Classify and categorize
    sentence_type = classify_sentence_type(bot_response)
    response_category = categorize_response(bot_response)

    return {
        "response": bot_response,
        "sentence_type": sentence_type,
        "response_category": response_category,
        "response_source": response_source,
        "similarity_score": score if match else 0,
        "context_used": bool(context)
    }