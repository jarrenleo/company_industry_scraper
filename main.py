import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd

company_names = []
primary_ssic_description = []
primary_user_described_activity = []

def read_csv(csv_file):
    # Read company names from csv file and store them into company_names[]
    with open(csv_file, "r", encoding="ISO-8859-1") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            company_names.append(row["Name"])

def find_url_path(soup, text):
    # Try to find the company name that matches the one in the csv file
    element = soup.find("a", text=text)
    if element:
        return element.get("href")
    else:
        # Else get the first company from the search results
        first_element = soup.find_all("a")[13]
        return first_element.get("href")

def get_url_path(company_name):
    # Convert company name to search parameter
    search_parameter = company_name.replace(" ", "+")
    response = requests.get(
        f"https://www.companies.sg/?NodeSearch%5Buen%5D=&NodeSearch%5Bentity_name%5D={search_parameter}")
    soup = BeautifulSoup(response.text, "lxml")

    return find_url_path(soup, company_name)

def find_description(soup, text, description_list):
    # Try to find the description header that matches the one we need
    element = soup.find("span", text=text)
    if element:
        description_list.append(element.find_next_sibling("label").get_text())
    else:
        # Else, set as no description
        description_list.append("")

def get_description(url_path):
    try:
        # If invalid url path, set as no description
        if not url_path.startswith("/"):
            primary_ssic_description.append("")
            primary_user_described_activity.append("")
            return

        response = requests.get(f"https://www.companies.sg{url_path}")
        soup = BeautifulSoup(response.text, "lxml")

        find_description(soup, "Primary Ssic Description",
                         primary_ssic_description)
        find_description(soup, "Primary User Described Activity",
                         primary_user_described_activity)
    except Exception as e:
        print(f"An error occcured: {e}")

def write_data_to_csv(csv_file):
    df = pd.read_csv(csv_file, encoding="ISO-8859-1")
    df["Primary SSIC Description"] = primary_ssic_description
    df["Primary User Described Activity"] = primary_user_described_activity
    df.to_csv(csv_file, index=False)

def get_data(csv_file):
    read_csv(csv_file)

    for company_name in company_names:
        print(company_name)
        url_path = get_url_path(company_name)
        get_description(url_path)

    write_data_to_csv(csv_file)

get_data("./Company_1.csv")