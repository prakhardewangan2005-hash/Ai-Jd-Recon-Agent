import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os

# --- Page Config ---
st.set_page_config(page_title="AI/ML JD Recon Agent", page_icon="🤖", layout="centered")

# --- Custom CSS for Premium Look ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; background-color: #ff4b4b; color: white; }
    .stTextInput>div>div>input { border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- Initialize Gemini API ---
# We use Streamlit Secrets to hide your API key securely
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash') # Fast and free
except Exception as e:
    st.error("⚠️ API Key not found. Please add GEMINI_API_KEY to Streamlit Secrets.")

# --- Scraper Function ---
def scrape_jd(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract main text (removing scripts and styles)
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator=' ', strip=True)
        return text[:5000] # Limit to 5000 chars to save token space
    except Exception as e:
        return f"Error scraping URL: {str(e)}"

# --- Main UI ---
st.title("🎯 Live AI/ML JD Recon Agent")
st.markdown("**Exclusive Intern Project:** Paste a live link to any AI/ML Job Description. The Agent will scrape it in real-time and generate a hyper-personalized Internship Action Plan & Cover Letter to help you land the role.")

jd_url = st.text_input("🔗 Paste Live Job Description URL (e.g., from YC, Lever, Greenhouse):", placeholder="https://boards.greenhouse.io/...")

if st.button("🚀 Run Recon & Generate Plan"):
    if not jd_url:
        st.warning("Please paste a URL first, bhai.")
    else:
        with st.spinner("🕵️‍♂️ Scraping live job posting..."):
            jd_text = scrape_jd(jd_url)
            
            if "Error" in jd_text:
                st.error("Failed to scrape. The site might be blocking bots. Try pasting the text directly instead.")
            else:
                st.success("✅ JD Scraped Successfully! Analyzing Tech Stack...")
                
                with st.spinner("🧠 Generating Custom Intern Action Plan..."):
                    prompt = f"""
                    You are an expert AI/ML technical recruiter. I am a student applying for an AI/ML internship.
                    I just scraped this live Job Description:
                    
                    {jd_text}
                    
                    Based on this exact JD, please provide:
                    1. **Core Tech Stack Identified:** A bulleted list of the exact AI/ML tools/languages they want.
                    2. **The "Show-Off" Mini-Project:** Suggest one highly specific weekend project I can build to impress them, using their exact tech stack.
                    3. **The Hook (Cover Letter Intro):** Write a 3-sentence, highly technical intro for an email/cover letter mentioning their tech stack and how I am learning it.
                    
                    Keep it professional, highly technical, and concise. No fluff.
                    """
                    
                    response = model.generate_content(prompt)
                    
                    st.divider()
                    st.subheader("📊 Your Recon Report")
                    st.markdown(response.text)
                    st.balloons()
