from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import sys
import os

# Load the chromium driver (with the link)
driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
# The URL to the website
URL = "http://164.100.47.194/Loksabha/Members/MemberAttendance.aspx"
# Open the webpage
driver.get(URL)
# To wait for the elements to be visible / rendered by the browser
wait = WebDriverWait(driver, 10)


def make_folder(path):
    """Helper function to make a folder
    
    Parameters
    ----------
    path : string
        path of the folder to create
    """    
    if not os.path.exists(path):
        os.mkdir(path)

# Path of the folder to save
save_folder = "./data/"
make_folder(save_folder)


# Find out the number of elements in the lok_sabha_term 
lok_sabha_term_elem_options_len = len(driver.find_elements_by_xpath('//*[@id="ContentPlaceHolder1_DropDownListLoksabha"]/option'))
# Always a good idea to add logging statement
print("Started scraping")
# Iterate over the number of elements present in the drop-down menu
for term_optNum in range(lok_sabha_term_elem_options_len):
    # Always a good idea for the elements to appear on the UI (to avoid exceptions)
    wait.until(EC.visibility_of_element_located((By.ID, "ContentPlaceHolder1_DropDownListLoksabha")))
    # Select element
    term_elem = driver.find_element_by_xpath('(//*[@id="ContentPlaceHolder1_DropDownListLoksabha"]/option)['+str(term_optNum+1)+']')
    # Extract the name of the element
    term_name = term_elem.get_attribute("text")
    # Logging statement
    print("Scraping for the term : {}".format(term_name))
    # Create a folder for the selected term of LS
    term_folder = save_folder + term_name + "/"
    make_folder(term_folder)
    # Select the element by using the click event
    term_elem.click()
    # Wait for it to load
    wait.until(EC.visibility_of_element_located((By.ID, "ContentPlaceHolder1_DropDownListLoksabha")))

    # Similarly, find number of sessions that took place for that term
    lok_sabha_session_elem_option_len = len(driver.find_elements_by_xpath('//*[@id="ContentPlaceHolder1_DropDownListSession"]/option'))
    # Iterate over the sessions
    for session_optNum in range(lok_sabha_session_elem_option_len):
        # Wait for the elements to appear on the UI
        wait.until(EC.visibility_of_element_located((By.ID, "ContentPlaceHolder1_DropDownListSession")))
        # Select the session element to select
        session_elem = driver.find_element_by_xpath('(//*[@id="ContentPlaceHolder1_DropDownListSession"]/option)['+str(session_optNum+1)+']')
        # Extract the text (for naming of the folder, logging and keeping a track of things)
        session_name = session_elem.get_attribute("text")
        # Logging statement
        print("Scraping for the session : {}".format(session_name))
        # Create a folder for the session of Lok Sabha
        session_folder = term_folder + session_name + "/"
        make_folder(session_folder)
        # Select the element to click
        session_elem.click()
        # Wait for the element to appear
        wait.until(EC.visibility_of_element_located((By.ID, "ContentPlaceHolder1_DropDownListSession")))

        # Now select the date for which we want the table to appear
        # Find out the number of available dates to choose from
        lok_sabha_session_date_elem_option_len = len(driver.find_elements_by_xpath('//*[@id="ContentPlaceHolder1_DropDownListDate"]/option'))
        # Iterate over all the dates and select the relevant items
        for date_optNum in range(lok_sabha_session_date_elem_option_len):
            # Wait for the elements to appear on the UI
            wait.until(EC.visibility_of_element_located((By.ID, "ContentPlaceHolder1_DropDownListDate")))
            # Select the date element
            date_elem = driver.find_element_by_xpath('(//*[@id="ContentPlaceHolder1_DropDownListDate"]/option)['+str(date_optNum+1)+']')
            # Get the text (ie. the date)
            date_name = date_elem.get_attribute("text")
            # Create a Pandas Dataframe where we will save the 
            df = pd.DataFrame()
            # The name list and the signature(attendance) list to be inserted in the dataframe
            name_list = []
            sign_list = []
            # Loggin statement
            print("Scraping for the date : {}".format(date_name))
            # Click on the current element
            date_elem.click()
            # Wait for the elements to appear on the UI
            wait.until(EC.visibility_of_element_located((By.ID, "ContentPlaceHolder1_DropDownListDate")))

            ### NOTE : Strange, when we select a new date on the final page (ie. 16)
            ### It maintains the state of the final page, therefore we will 
            # have to ensure that we also start with the first page, coding this functionality
            # Select the page row
            first_page_check = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_DataGrid1"]/tbody/tr[1]/td').find_elements_by_tag_name("a")
            # There are some cases in which a parliament date was present, but the meet eventually didn't take place
            # or there is no data available for the same, therefore handling that case
            if len(first_page_check)!=0:
                first_page_check = first_page_check[0]
            else:
                break
            # Checking whether we are starting from the first page or not
            if first_page_check.text=='1':
                first_page_check.click()
                wait.until(EC.visibility_of_element_located((By.ID, "ContentPlaceHolder1_tblMember")))

            # Getting all the relevant rows from the table (of the users)
            # The exact numbers are based on trying and testing, plase play around with the HTML
            member_table_element_all_rows = driver.find_elements_by_xpath('//*[@id="ContentPlaceHolder1_DataGrid1"]/tbody/tr')
            required_info = member_table_element_all_rows[2:-1]
            # Iterate through the rows of the table
            for name_counter in range(len(required_info)):
                # Get all the words in the table row
                curr = required_info[name_counter].text.split()
                # String which stores the name
                name_s = ""
                for row in range(2,len(curr)-2):
                    name_s += (curr[row] + " ")
                name_s += curr[len(curr)-2]
                sign_s = curr[-1]
                name_list.append(name_s) # Append the name in the name list
                sign_list.append(sign_s) # Append the signature in the signature list
            
            # The pages href's do not throw all the links, therefore we maintain a counter for the same
            link_counter = 0 # This will maintain the counter for the page to navigate to
            
            # Iterate through all the page
            while(1):
                # Get all the pages
                all_pages = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_DataGrid1"]/tbody/tr[1]/td').find_elements_by_tag_name("a")
                # if we have visited all the pages, break the loop
                if (link_counter >= len(all_pages)):
                    break
                # Next link to visit
                next_link = all_pages[link_counter]
                # Logging statement (of visiting a particular page)
                print("Clicking the link : {}".format(next_link.text))
                link_counter+=1
                # Click on the page
                next_link.click()
                # Wait for the table to actually appear and get rendered by the JS
                wait.until(EC.visibility_of_element_located((By.ID, "ContentPlaceHolder1_tblMember")))
                # Similar functionality of actually getting all the users
                member_table_element_all_rows = driver.find_elements_by_xpath('//*[@id="ContentPlaceHolder1_DataGrid1"]/tbody/tr')
                required_info = member_table_element_all_rows[2:-1]
                for name_counter in range(len(required_info)):
                    curr = required_info[name_counter].text.split()
                    name_s = ""
                    for row in range(2,len(curr)-2):
                        name_s += (curr[row] + " ")
                    name_s += curr[len(curr)-2]
                    sign_s = curr[-1]
                    name_list.append(name_s)
                    sign_list.append(sign_s)
            # Log the number of names that are present in the table
            print("size of name list : ", len(name_list))
            # Log the number of signatures present in the list
            print("size of sign list : ", len(sign_list))
            # Add the two lists under relevant name in the Pandas DataFrame
            df["Name"] = name_list
            df["Signed"] = sign_list
            # Log the Saving of a CSV
            print("Saving " + session_folder + date_name + ".csv")
            # Save the CSV file with the name as the date of the proceedings under relevant folders
            df.to_csv(session_folder + date_name + ".csv", index=False)