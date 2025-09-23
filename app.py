import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from openai import OpenAI
import os
from dotenv import load_dotenv
import time

# Load OpenAI API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Validate API key
if not api_key:
    st.error("No API key found. Please check your .env file.")
elif not api_key.startswith("sk-proj-"):
    st.warning("API key found, but it doesn't start with 'sk-proj-'. Double-check your key.")
elif api_key.strip() != api_key:
    st.warning("API key may have leading or trailing spaces. Please clean it up.")
else:
    st.success("API key loaded successfully.")

# Initialize OpenAI client
openai = OpenAI(api_key=api_key)

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
def get_reviews(url, review_selector=".comments-from-verified-purchases .feedback"):
	driver = setup_driver()
	driver.get(url)

#waiting for review to load
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
		WebDriverWait(driver, 15).until(
			EC.presence_of_all_elements_located((By.CSS_SELECTOR, review_selector))
	)
	except Exception as e:
		pass
	review_elements = driver.find_elements(By.CSS_SELECTOR, review_selector)
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
st.write("Enter a product URL to get a summary of customer feedback.")

url = st.text_input("Product URL")

if st.button("Analyze"):
    if url:
        with st.spinner("Scraping reviews and generating summary..."):
            reviews = get_reviews(url)
            if reviews:
                st.subheader("Individual Reviews")
                for i, review in enumerate(reviews, start=1):
                    st.markdown(f"**Review #{i}:** {review}")
                st.subheader("AI Summary")
                summary = summarize_reviews(reviews)
                st.markdown(summary)
            else:
                st.error("No reviews found. Try a different product or check the page structure.")
    else:
        st.warning("Please enter a valid product URL.")