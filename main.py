from fastapi import FastAPI, UploadFile, File
from typing import List
import os
from dotenv import load_dotenv
from document_processor import DocumentProcessor
import openai
import ast
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

load_dotenv()

app = FastAPI()
document_processor = DocumentProcessor()

# Google Form URL (replace with your actual form URL)
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSemlBSMvQsQZnAudDXMWXGldJGdZW6VkoDAwbQKsuTGlgZfNg/viewform"

@app.post("/upload-documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    parsed_documents = []  # Reset the list for new uploads

    for file in files:
        file_path = f"data/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Process the document and extract text
        chunks = document_processor.process_document(file_path)
        parsed_documents.extend(chunks)  # Store the extracted text

    # Combine the parsed documents into a single context
    context = "\n".join(parsed_documents)
    print("context", context)

    # Use OpenAI to extract specific information
    prompt = (
        "Important, don't type anything else. just give key value pair. Format {'key': 'value'}. Use date as 01/01/2025. average_gross weight as 100 and average_price as 100. Assume other data, which you are not able to find. Extract the following information from the text:\n"
        "1. Bill of lading number\n"
        "2. Container Number\n"
        "3. Consignee Name\n"
        "4. Consignee Address\n"
        "5. Date\n"
        "6. Line Items Count\n"
        "7. Average Gross Weight\n"
        "8. Average Price\n\n"
        f"Text:\n{context}\n\n"
        "Return the extracted information in the following format:\n"
        "{\n"
        "  'bill_of_lading_number': '...',\n"
        "  'container_number': '...',\n"
        "  'consignee_name': '...',\n"
        "  'consignee_address': '...',\n"
        "  'date': '...',\n"
        "  'line_items_count': '...',\n"
        "  'average_gross_weight': '...',\n"
        "  'average_price': '...'\n"
        "}"
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Get the AI response
    ai_response = response.choices[0].message.content
    print("AI Response:", ai_response)  # Print the AI response for debugging

    # Convert the extracted information to a dictionary using ast.literal_eval
    form_data = {}
    try:
        form_data = ast.literal_eval(ai_response)  # Safely evaluate the string to a dictionary
    except Exception as e:
        return {"success": "false", "error": "Failed to parse AI response."}  # Return false if parsing fails

    # Debugging: Print the parsed form_data
    print("Parsed Form Data:", form_data)  # Add this line to see the parsed data

    # Check if all required fields are present
    required_fields = [
        'bill_of_lading_number',
        'container_number',
        'consignee_name',
        'consignee_address',
        'date',
        'line_items_count',
        'average_gross_weight',
        'average_price'
    ]

    # Debugging: Print the required fields and check against form_data
    print("Required Fields:", required_fields)  # Add this line to see the required fields
    print("Form Data Keys:", form_data.keys())  # Add this line to see the keys in form_data

    if not all(field in form_data for field in required_fields):
        return {"success": "false", "error": "Missing required fields."}  # Return false if any required field is missing

    # Use Selenium to fill out the Google Form
    try:
        # Set up Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
        
        # Specify the path to your ChromeDriver
        service = Service("/Users/shivambangia/Downloads/chromedriver/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Open the Google Form
        driver.get(GOOGLE_FORM_URL)

        # Fill out the form fields
        driver.find_element(By.XPATH, "//input[@aria-label='Bill of lading number']").send_keys(form_data.get('bill_of_lading_number', ''))
        driver.find_element(By.XPATH, "//input[@aria-label='Container Number']").send_keys(form_data.get('container_number', ''))
        driver.find_element(By.XPATH, "//input[@aria-label='Consignee Name']").send_keys(form_data.get('consignee_name', ''))
        driver.find_element(By.XPATH, "//input[@aria-label='Consignee Address']").send_keys(form_data.get('consignee_address', ''))
        driver.find_element(By.XPATH, "//input[@aria-label='Date']").send_keys(form_data.get('date', ''))
        driver.find_element(By.XPATH, "//input[@aria-label='Line Items Count']").send_keys(form_data.get('line_items_count', ''))
        driver.find_element(By.XPATH, "//input[@aria-label='Average Gross Weight']").send_keys(form_data.get('average_gross_weight', ''))
        driver.find_element(By.XPATH, "//input[@aria-label='Average Price']").send_keys(form_data.get('average_price', ''))

        # Submit the form
        driver.find_element(By.XPATH, "//span[text()='Submit']").click()  # Adjust the XPath as needed

        time.sleep(2)  # Wait for a moment to ensure the form is submitted

        return {"success": "true"}  # Return true if the form submission is successful
    except Exception as e:
        return {"success": "false", "error": str(e)}  # Return false if an exception occurs
    finally:
        if 'driver' in locals() and driver is not None:
            driver.quit()  # Close the browser