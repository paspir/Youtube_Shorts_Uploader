# main.py
import random
from datetime import datetime, timedelta
import time
from AccountData import account_data
from pytube import YouTube
from googleapiclient.discovery import build
import os, string
from moviepy.editor import VideoFileClip, afx
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pyperclip
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
from pytube.exceptions import VideoUnavailable

SAVE_PATH = "path_to_videos_folder"

def UploadVideo(password, email, link, proxy, api_key, query_keywords):
    # Your video upload logic here
    print(f"Uploading video for {email}")
    print(f"Video Link: {link}")
    print(f"Using Proxy: {proxy}")
    print(f"API Key: {api_key}")
    print(f"Query Keywords: {query_keywords}")

    selected_short = None
    original_video_url = None
    edited_video_path = None
    original_video_name = None
    da= False

        # List to keep track of all the tried video URLs
    tried_video_urls = []

    #Get the Short
    shorts = get_shorts(api_key, query_keywords)

        
    print('Starting Next Upload')

    while True:                                                                                                                                                             

        while shorts:
                            # Choose a random Short from our search
            selected_short = random.choice(shorts)
            original_video_url = selected_short["url"]

            # Check if the video URL has already been tried
            if original_video_url in tried_video_urls:
                print("Video URL already tried. Trying another...")
                shorts.remove(selected_short)  # Remove from the list to try another one
                continue

            else:
                            # Add the video URL to the list of tried video URLs
                tried_video_urls.append(original_video_url)
                print("Selected Minecraft Short:", selected_short["title"])
                print("URL:", original_video_url)

                try:
                    # Download the video and get the downloaded path
                    downloaded_path = download_video(original_video_url, SAVE_PATH)
                    original_video_name = returnTitle(original_video_url)

                    # Check if the download was successful
                    if downloaded_path is not None:
                        print("Downloaded Video Path:", downloaded_path)

                        # Generate a random three-digit number
                        random_number = generate_random_number()

                        # Rename the video file with the new name
                        new_video_name = f"video{random_number}.mp4"
                        new_video_path = os.path.join(SAVE_PATH, new_video_name)
                        os.rename(downloaded_path, new_video_path)

                        print("New Video Path:", new_video_path)

                        # Edit the video
                        edited_video_path = editVideo(new_video_path)
                        print("Edited Video Path:", edited_video_path)

                        input("snag the vid...")

                        break  # Break out of the inner loop if the download and edit are successful
                except Exception as e:
                    print(e)
                    time.sleep(1)
                    #If list is now empty and our last one failed break
                    if not shorts:
                        da = True
                        break

        # Break if we were excied and no more - redundant 
        if da:
            da = False
            break 


        try:
            
            video_description = f"""
👋 Hey there, YouTube fam! Welcome to our channel! 🎉 

🎥 Original Video: {original_video_url}

💡 Remember to like and subscribe to our channel for more awesome content like this! 😊 By hitting that subscribe button and tapping the notification bell, you'll never miss out on any of our future uploads.

🔔 Stay tuned for more exciting videos coming your way! Don't forget to share this video with your friends and family to spread the awesomeness. We appreciate your support! 🙏

#LikeAndSubscribe #SupportCreators
            
            """

            # Call the function to open the YouTube login page
            youtubeUpload(edited_video_path, video_description, password, email, link, proxy, original_video_name)  #, proxy)


            
            # tiktokUpload(edited_video_path, original_video_name)

            #remove the downloaded vid & the edited one
            os.remove(edited_video_path) 
            os.remove(new_video_path)
            break
        except Exception as e:
            #remove the video
            
            print(e)
            print('sleeping 30 to copy')
            time.sleep(30)
                    # Check if the error is due to exceeding the quota
            if "quotaExceeded" in str(e):
                message = ("Minecraft Clips - Quota Limit Exceeded. Waiting until midnight...")
                print(message)

                time_remaining = time_until_midnight()
                time.sleep(time_remaining)  # Wait until midnight

            #remove the downloaded vid & the edited one
            os.remove(edited_video_path)
            os.remove(new_video_path)


            if not shorts:
                        break

    return

def generate_random_number():
    return ''.join(random.choices(string.digits, k=3))

def time_until_midnight():
    now = datetime.datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    time_remaining = (midnight - now).total_seconds()
    return time_remaining

def editVideo(video_path):
    # Load the video clip
    clip = VideoFileClip(video_path)

    # Edit the pitch randomly between 0.9 to 1.1 of the original pitch
    pitch_factor = random.uniform(0.93, 1.07)
    # Note: We have removed the line that edits pitch here, as we'll handle pitch adjustment differently

    # Make the video faster randomly between 1.1 to 1.3 speed
    speed_factor = random.uniform(1.03, 1.08)
    clip = clip.speedx(speed_factor)

    # Split the audio and video parts
    audio = clip.audio
    video = clip.without_audio()

    # Apply audio volume multiplication using volumex
    volume_factor = random.uniform(0.8, 1.2)
    audio = audio.fx(afx.volumex, volume_factor)

    # Combine the video with the adjusted audio
    edited_clip = video.set_audio(audio)

    # Save the edited video to a new file
    edited_video_path = video_path.replace(".mp4", "_edited.mp4")
    edited_clip.write_videofile(edited_video_path, codec="libx264", audio_codec="aac")

    # Close the clips
    clip.close()
    edited_clip.close()

    return edited_video_path


def main():

    while True:
        try:
            account = random.choice(account_data)
            password = account['password']
            email = account['email']
            link = account['link']
            proxy = account['proxy']
            api_key = account['api_key']
            query_keywords = account['query_keywords']
            UploadVideo(password, email, link, proxy, api_key, query_keywords)
        
            print("Waiting for 30  minutes before the next upload...")
            # time.sleep(60 * 30)  # Sleep for 10 minutes (600 seconds)
            time.sleep(5) #upload speed demon for now

        except Exception as e:
            print(e)
            time.sleep(30)
        


def returnTitle(link):
    try:
        yt = YouTube(link)
        return yt.title
    except Exception as e:
        print(f"Some Error! : {e}")
        return None

def download_video(link, save_path):
    try:
        yt = YouTube(link)
    except Exception as e:
        print(f"Some Error! : {e}")
        return None

    # Check if the video is age-restricted
    if yt.age_restricted:
        print("Selected video is age-restricted. Unable to download.")
        return None
    
    try:
        print("do our print")
        print(yt.streams.filter(file_extension='mp4').all())
        video_stream = yt.streams.filter(file_extension='mp4').get_highest_resolution()
    except VideoUnavailable as e:
        print(f"Video is unavailable: {e}")
        return None
    except Exception as e:
        print(f"Some other error occurred: {e}")
        return None

    try:
        video_stream.download(save_path)
        downloaded_path = os.path.join(save_path, video_stream.default_filename)
        print('Task Completed!')
        return downloaded_path
    except Exception as e:
        print(f"Some Error! 2 : {e}")
        return None

def get_shorts(api_key, keywords):
    api_service_name = "youtube"
    api_version = "v3"
    youtube = build(api_service_name, api_version, developerKey=api_key)

    try:
        if not keywords:
            print("No keywords provided.")
            return []

        # Calculate the date 3 months ago from today
        three_months_ago = datetime.now() - timedelta(days=90)
        published_after_date = three_months_ago.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Make the API request to search for Minecraft shorts
        search_response = youtube.search().list(
            q=random.choice(keywords),  # Select a random keyword from the provided list
            part="snippet",
            type="video",
            videoDuration="short",  # Filter for short videos only
            order="viewCount",      # Sort by view count to get most popular ones
            maxResults=500,          # Limit the results to 500 (adjust as needed)
            publishedAfter=published_after_date
        ).execute()

        # Extract video IDs and other details of the Minecraft shorts
        minecraft_shorts = []
        for item in search_response["items"]:
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            video_url = f"https://www.youtube.com/shorts/{video_id}"  # Use the correct format
            minecraft_shorts.append({"title": title, "url": video_url})


        return minecraft_shorts

    except Exception as e:
        print("An error occurred:", e)
        return []
    
    # Function to introduce random delays between actions
def random_delay():
    time.sleep(random.uniform(0.8, 2))

def mini_delay():
    time.sleep(random.uniform(0.3, 0.5))

def handle_youtube_studio_app_advertisement(driver):
    try:
        # Wait up to 10 seconds for the "Continue to Studio" button to be present and visible
        continue_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@class='button continue-to-studio black-secondary']"))
        )

        # Check if the "Continue to Studio" button is displayed (visible on the page)
        if continue_button.is_displayed():
            print("The 'Continue to Studio' button is visible. Clicking it to bypass the advertisement...")
            # Click the "Continue to Studio" button
            continue_button.click()
            print("Clicked 'Continue to Studio' button to bypass the advertisement.")
            # Wait for the YouTube Studio page to load (adjust the delay if needed)
            time.sleep(15)
            return

    except:
        print("Advertisement not found or not visible on the page. Proceeding without clicking.")
        return
    
# Function to simulate human-like typing
def human_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))
    
def type_email(driver, email):
    try:
        # Find the email input box by its ID
        email_input = driver.find_element(By.ID, 'identifierId')

        # Clear the input box in case there is any pre-existing text
        email_input.clear()

        # type email
        human_typing(email_input, email)

        random_delay()
        #click next
        email_input.send_keys(Keys.ENTER)
        random_delay()

    except Exception as e:
        print(f"An error occurred while typing the email: {e}")

def check_element_visibility(driver, locator, timeout=10):
    try:
        # Wait for the element to be visible on the screen
        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.visibility_of_element_located(locator))
        
        # Check if the element is displayed on the screen
        if element.is_displayed():
            print("The element is on the screen.")
            return True
        else:
            print("The element is not visible on the screen.")
            return False
    
    except TimeoutException:
        print("Timeout: The element is not visible on the screen.")
        return False
    
    except NoSuchElementException:
        print("Element not found.")
        return False
    
# Method to type password into the password input box
def type_password(driver, password):
    try:
        # Find the password input box by its name attribute
        password_input = driver.find_element(By.NAME, 'Passwd')

        # Clear the input box in case there is any pre-existing text
        password_input.clear()

        # Simulate human-like typing of the password using the human_typing function
        human_typing(password_input, password)

        random_delay()
                # Press Enter to login
        password_input.send_keys(Keys.ENTER)
        random_delay()

    except Exception as e:
        print(f"An error occurred while typing the password: {e}")

def youtubeUpload(file_path, video_description, password, email, link, proxy, original_video_name):    #, proxy):

    notLogged = True

    try:
        while True:
            

                        #New fixed
            chrome_options = uc.ChromeOptions()
            # chrome_options.user_data_dir = "c:\\temp\\profile"
            if proxy != 'localhost:8080':
                print("doing proxy")
                chrome_options.add_argument('--proxy-server=%s' % proxy)
            else:
                print("skipped prxy")
            # chrome_options.add_argument('--headless')
            # chrome_options.add_argument('--disable-gpu')  # This might be necessar
            driver = uc.Chrome(options=chrome_options, driver_executable_path=r'C:\Users\ben13\OneDrive\Documents\vsCodeDirect\chrome-win64\chromedriver.exe')
            # driver = uc.Chrome(options=chrome_options)


            mini_delay()
            # Open YouTube login page
            driver.get(link)

            # time.sleep(330)
            # input("Press Enter to continue...") #Use this when need to login, if ever

            random_delay()
            # Check if FILES 
                        #Check for the studio add
            handle_youtube_studio_app_advertisement(driver)
            random_delay()

                        # Find and click the "Select files" button
            try:
                # Find and click the "Select files" button
                select_files_button = driver.find_element(By.ID, "select-files-button")
                mini_delay()
                select_files_button.click()
                print("Already Logged in")
                notLogged = True
                break
            except NoSuchElementException:
                print("NEed to log")
                


            # Wait for the page to load
            random_delay()

            type_email(driver, email)

            random_delay()

            # Locate the element with the specified text
            element_text = "Try using a different browser. If you’re already using a supported browser, you can try again to sign in."
            element_locator = (By.XPATH, f"//*[contains(text(), '{element_text}')]")

            # Call the function to check element visibility
            element_found = check_element_visibility(driver, element_locator)

            if not element_found:
                random_delay()
                break
            else:
                random_delay()
                driver.quit()  # Close the current driver
                continue  # Start a new iteration with a new driver
                

        if notLogged:
            print("We're in the main part of code:")



            random_delay()

            type_password(driver, password)

            random_delay()

            #Check for the studio add
            handle_youtube_studio_app_advertisement(driver)

            # Find and click the "Select files" button
            try:
                # Find and click the "Select files" button
                select_files_button = driver.find_element(By.ID, "select-files-button")
                select_files_button.click()
                print("Clicked the 'Select files' button successfully.")
                notLogged = False
            except NoSuchElementException:
                print("The 'Select files' button is not present on the page.")
                notLogged = False

        random_delay()

        # input("press enter..")
        select_file_for_upload(file_path, driver)

        time.sleep(5)
        random_delay()

        fillOutVidDetails(driver, video_description, original_video_name)

        # Wait for the login page to load
        print(f"Video Upload Loop Complete")

        # Now you should be on the YouTube login page and ready to proceed with the rest of your code for authentication and video upload.

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser window
        driver.quit()
        pass

def type_with_random_delay(text, min_delay=0.01, max_delay=0.02):
    for char in text:
        pyautogui.write(char)
        time.sleep(random.uniform(min_delay, max_delay))
        pyautogui.press('right')  # Move the cursor right to mimic human-like typing

def fillOutVidDetails(driver, video_description, original_video_name):
    # Assuming the driver is used to interact with the web page containing the title element
    # Randomly select one title from the list

    try:
        # Check if the element is visible on the screen
        error_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@class="error-short style-scope ytcp-uploads-dialog" and text()="Daily upload limit reached"]'))
        )

        if error_element.is_displayed():
            print("The 'Daily upload limit reached' error is visible on the screen ")
            return 

    except Exception as e:
        pass

    
    #re-use button
    try:
        reuse_details_button = driver.find_element(By.ID, "reuse-details-button")

        # Check if the button is clickable
        if reuse_details_button.is_enabled():
            # Scroll to the button element
            driver.execute_script("arguments[0].scrollIntoView();", reuse_details_button)
            time.sleep(random.uniform(1, 3))

            # Click the button
            reuse_details_button.click()
            random_delay()
            time.sleep(5)
            
    except Exception as e:
        print("Clicking the reuse details button failed.")
        print(e)
        return

    #second card
    try:
                # Find all the video cards
        video_cards = driver.find_elements(By.XPATH, "//ytcp-entity-card[@class='card style-scope ytcp-video-pick-dialog-contents']")

        # Check if there is at least a second video card
        if len(video_cards) >= 2:
            # Click on the second video card
            video_cards[1].click()

        random_delay()
        time.sleep(random.uniform(4,6))
            
    except Exception as e:
        print(e)
        return
    
        # Find the "Close" button by its class name and check if it's visible.
    try:
        close_button = driver.find_element(By.XPATH, "//div[@class='label style-scope ytcp-button' and text()='Close']")
        if close_button.is_displayed():
            close_button.click()
            print("Close button clicked successfully!")
        else:
            print("Close button is not visible on the screen.")
    except NoSuchElementException:
        print("Close button element not found on the page.")


    #submit re-use
    try:
        # Find the "Reuse" button by its ID and click it.
        reuse_button = driver.find_element(By.ID, 'select-button')
        reuse_button.click()
        random_delay()
    except Exception as e:
        print(e)
        return


    try: # try to do title
        # video_title = random.choice(generic_titles)
        video_title = original_video_name

        # Disable the fail-safe
        pyautogui.FAILSAFE = False
        # Wait for a moment before typing the title (adjust the delay if needed)
        pyautogui.sleep(random.uniform(0.5, 2))

        # Find all elements with the same ID (multiple elements can have the same ID)
        textbox_elements = driver.find_elements(By.ID, "textbox")

        # First textbox is for the title
        title_element = textbox_elements[0]

        # Click on the title element to ensure it has focus
        title_element.click()

        time.sleep(random.uniform(1, 3))
                # Move the cursor to the beginning of the text
        title_element.send_keys(Keys.HOME)
        random_delay
        # Select all text in the description box and delete it
        title_element.send_keys(Keys.CONTROL, 'a')  # Select all text
        random_delay
        title_element.send_keys(Keys.DELETE)  # Delete selected text
        random_delay
        # Use pyperclip to copy the text to the clipboard
        pyperclip.copy(video_title)
        # Simulate Ctrl+V (Command+V on Mac) to paste the text
        title_element.send_keys(Keys.CONTROL, 'v')

        time.sleep(random.uniform(1, 3))
        random_delay()
        # Simulate pressing the Enter key to remove focus from the title element
        title_element.send_keys(Keys.ENTER)
        random_delay()
        random_delay()

    except Exception as e:
        print("Title Failed - Exiting")
        print(e)
        return

    try: # try to do desc
    # Try to do desc
        # Second textbox is for the description
        description_element = textbox_elements[1]

        # Click on the description element to ensure it has focus
        description_element.click()
        random_delay()

        # Use pyperclip to copy the description to the clipboard
        pyperclip.copy(video_description)

        # Select all text in the description box and delete it
        description_element.send_keys(Keys.CONTROL, 'a')  # Select all text
        description_element.send_keys(Keys.DELETE)  # Delete selected text

        # Simulate Ctrl+V (Command+V on Mac) to paste the description
        description_element.send_keys(Keys.CONTROL, 'v')
        random_delay()

        random_delay()

    except Exception as e:
        print("desc Failed")
        print(e)
        return


    try: # try to do radio for kids
        # Find all radio button elements with the same ID (multiple elements can have the same ID)
        radio_buttons = driver.find_elements(By.ID, "offRadio")
        
        # Check if the second radio button exists in the list before interacting with it
        if len(radio_buttons) >= 2:
            # Get the second radio button element from the list
            second_radio_button = radio_buttons[1]
            
            time.sleep(random.uniform(1, 3))

            # Scroll to the radio button element
            driver.execute_script("arguments[0].scrollIntoView();", second_radio_button)
            time.sleep(random.uniform(1, 3))
            # Click the radio button
            second_radio_button.click()
        else:
            print("Second radio button not found.")

    except Exception as e:
        print("radio Failed")
        print(e)
        return

    try: # try to do submit
        # Find the submit button element by its ID (assuming it's "next-button")
        submit_button = driver.find_element(By.ID, "next-button")
        
        # Scroll to the submit button element
        driver.execute_script("arguments[0].scrollIntoView();", submit_button)
        time.sleep(random.uniform(1, 3))
        # Click the submit button
        submit_button.click()
        time.sleep(random.uniform(1, 3))

    except Exception as e:
        print("next Failed")
        print(e)
        return

    try: # try to do submit 2
        # Find the second "Next" button element by its ID (assuming it's "next-button")
        second_next_button = driver.find_element(By.ID, "next-button")
        time.sleep(random.uniform(1, 3))
        # Scroll to the second "Next" button element
        driver.execute_script("arguments[0].scrollIntoView();", second_next_button)
        time.sleep(random.uniform(1, 3))
        # Click the second "Next" button
        second_next_button.click()

    except Exception as e:
        print("next2 Failed")
        print(e)
        return

    try: # try to do submit 3
        # Find the third "Next" button element by its ID (assuming it's "next-button")
        third_next_button = driver.find_element(By.ID, "next-button")
        time.sleep(random.uniform(1, 3))
        # Scroll to the third "Next" button element
        driver.execute_script("arguments[0].scrollIntoView();", third_next_button)
        time.sleep(random.uniform(1, 3))
        # Click the third "Next" button
        third_next_button.click()

    except Exception as e:
        print("next3 Failed")
        print(e)
        return

    try: # try to do radio for kids
        # Find all radio button elements with the same ID (multiple elements can have the same ID)
        radio_buttons = driver.find_elements(By.ID, "offRadio")
        
        # Check if the fourth radio button exists in the list before interacting with it
        if len(radio_buttons) >= 4:
            # Get the fourth radio button element from the list
            fourth_radio_button = radio_buttons[3]
            
            time.sleep(random.uniform(1, 3))

            # Scroll to the radio button element
            driver.execute_script("arguments[0].scrollIntoView();", fourth_radio_button)
            time.sleep(random.uniform(1, 3))
            # Click the radio button
            fourth_radio_button.click()
        else:
            print("Fourth radio button not found.")

    except Exception as e:
        print("radio Failed")
        print(e)
        return

    try: # try to do last submit
        # Find the "Publish" button element by its ID (assuming it's "done-button")
        publish_button = driver.find_element(By.ID, "done-button")
        time.sleep(random.uniform(1, 3))
        # Scroll to the "Publish" button element
        driver.execute_script("arguments[0].scrollIntoView();", publish_button)
        time.sleep(random.uniform(1, 3))
        # Click the "Publish" button
        publish_button.click()

    except Exception as e:
        print("Publish button Failed")
        print(e)
        return

    try: # Try to SAVE instead incase something went wrong
        # Find the fourth "Next" button element by its ID (assuming it's "next-button")
        fourth_next_button = driver.find_element(By.ID, "next-button")
        time.sleep(random.uniform(1, 3))
        # Scroll to the fourth "Next" button element
        driver.execute_script("arguments[0].scrollIntoView();", fourth_next_button)
        time.sleep(random.uniform(1, 3))
        # Click the fourth "Next" button
        fourth_next_button.click()

    except Exception as e:
        print("next4 Failed")
        print(e)
        return



def select_file_for_upload(file_path, driver):
    # Ensure the file path exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The specified file path does not exist: {file_path}")

    # Wait for a moment before typing the file path (adjust the delay if needed)
    pyautogui.sleep(random.uniform(0.5, 2))

     # Type the file path with random delays between characters and keypresses
    type_with_random_delay(file_path)

    # Introduce a brief delay before pressing Enter (adjust the delay if needed)
    pyautogui.sleep(random.uniform(0.5, 1))

    # Press Enter
    pyautogui.press("enter")

    # Wait for a moment to allow the file explorer window to open (adjust the delay if needed)
    pyautogui.sleep(random.uniform(1, 2))

    # Check if the video title element is present - OLD
    # upload_screen = is_video_title_present(driver)

    # # If the video title element is not present, type the file path again
    # if not is_file_explorer_open(driver):
    #     print("*********We got in")
    #     type_with_random_delay(file_path) 
    #     pyautogui.sleep(random.uniform(0.5, 1))
    #     pyautogui.press("enter")

    # Wait for the Video to upload window to open (adjust the delay if needed)
    pyautogui.sleep(15)

def is_file_explorer_open(driver):
    try:
        # Wait up to 10 seconds for the element to be present and visible
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#title.style-scope.ytcp-uploads-dialog"))
        )

        # Check if the element is displayed (visible on the page)
        if element.is_displayed():
            print("File explorer is open.")
            return False
        else:
            print("File explorer is not open.")
            return True

    except:
        print("Error occurred while checking file explorer status.")
        return True

if __name__ == "__main__":
    main()
