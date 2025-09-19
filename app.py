import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from openai import OpenAI
import os
from dotenv import load_dotenv
import time

# Load OpenAI API key
load_dotenv()
api_key = st.secrets["OPENAI_API_KEY"]
openai = OpenAI(api_key=api_key)

# Validate API key
if not api_key:
    st.error("No API key found. Please check your .env file.")
elif not api_key.startswith("sk-proj-"):
    st.warning("API key found, but it doesn't start with 'sk-proj-'. Double-check your key.")
elif api_key.strip() != api_key:
    st.warning("API key may have leading or trailing spaces. Please clean it up.")
else:
    st.success("API key loaded successfully.")


# Set up Selenium driver
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.binary_location = "/usr/bin/chromium"

    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=chrome_options)

# Scrape reviews from product page
def get_reviews(url, review_class="review-text"):
    driver = setup_driver()
    driver.get(url)
    time.sleep(3)
    review_elements = driver.find_elements(By.CLASS_NAME, review_class)
    reviews = [r.text for r in review_elements if r.text.strip()]
    driver.quit()
    return reviews

# Summarize reviews using OpenAI
def summarize_reviews(reviews):
    messages = [
        {"role": "system", "content": "You are a helpful assistant that summarizes customer reviews for products."},
        {"role": "user", "content": "Summarize the following product reviews:\n\n" + "\n".join(reviews)}
    ]
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content

# Streamlit UI
st.set_page_config(page_title="Product Review Analyzer")
st.title("Product Review Analyzer")
st.write("Enter a product URL and review class name to get a summary of customer feedback.")

url = st.text_input("Product URL")
review_class = st.text_input("Review Class Name", value="review-text")

if st.button("Analyze"):
    if url:
        with st.spinner("Scraping reviews and generating summary..."):
            reviews = get_reviews(url, review_class)
            if reviews:
                st.subheader("Individual Reviews")
                for i, review in enumerate(reviews, start=1):
                    st.markdown(f"**Review #{i}:** {review}")
                st.subheader("AI Summary")
                summary = summarize_reviews(reviews)
                st.markdown(summary)
            else:
                st.error("No reviews found. Try a different class name or check the URL.")
    else:
        st.warning("Please enter a valid product URL.")
