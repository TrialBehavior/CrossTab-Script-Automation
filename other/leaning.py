import pdfplumber
import streamlit as st
import re

# Juror class to hold the extracted data
class Juror:
    def __init__(self, name, gender, age, education, marital_status, race, occupation, final_leaning):
        self.name = name
        self.gender = gender
        self.age = age
        self.education = education
        self.marital_status = marital_status
        self.race = race
        self.occupation = occupation
        self.final_leaning = final_leaning

# Function to parse each row into a Juror object
def parse_row(row):
    if row is None:
        return None
    row = cleanText(row)
    lines = [line.strip() for line in row.split('\n') if line.strip()]
    i = 2 if lines[1] == '*' else 1
    name = lines[i] 
    gender = lines[i+1].split(': ')[1]
    age = int(lines[i+2].split(': ')[1])
    education = lines[i+3].split(': ')[1]
    marital_status = lines[i+4].split(': ')[1]
    race = lines[i+5].split(': ')[1]
    occupation = lines[i+6]
    final_leaning = lines[i+7].split(': ')[1]
    # Create and return a Juror object
    return Juror(name, gender, age, education, marital_status, race, occupation, final_leaning)
def cleanText(row):
    return re.sub('(\(cid:\d+\)|\*|\.)','',row)


# Load the PDF and extract tables
def extract(pdf):
    uploaded_file = pdf  # Replace this with the actual file path
    print(uploaded_file)
    with pdfplumber.open(uploaded_file) as pdf:
        num_pages = len(pdf.pages)
        for i in range(num_pages):
            page = pdf.pages[i]
            tables = page.extract_tables()
            
            print(f"Found {len(tables)} tables")
            
            # Create a list to store juror objects
            jurors = []

            # Loop through each table (in case there are multiple)
            for i, table in enumerate(tables):
                print(f"Table {i+1}:")
                for row in table:
                    for innerrow in row:
                        juror = parse_row(innerrow)
                        if juror != None:
                            juror.final_leaning = juror.final_leaning[0]
                            jurors.append(juror)
    return jurors


    
    