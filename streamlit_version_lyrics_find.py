import requests
from bs4 import BeautifulSoup
import webbrowser
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import streamlit as st

def find_lyrics_link(website, singer, song):
    # Format the query string
    query = f"{singer} {song}".replace(' ', '+')
    # Ensure the website variable is correctly formatted for the Google search
    formatted_website = website.replace('https://', '').replace('http://', '').rstrip('/')
    url = f"https://www.google.com/search?q=site:{formatted_website}+{query}"
    
    # Send the HTTP request
    response = requests.get(url)
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all the search result links
    links = soup.find_all('a')
    
    # Extract and return the first relevant link
    for link in links:
        href = link.get('href')
        if href and "url?q=" in href and not "webcache" in href:
            # Extract the URL from the Google redirect URL
            start = href.find("url?q=") + 6  # Adjust for the length of "url?q="
            end = href.find("&sa=U", start)
            clean_url = href[start:end]
            # Check if the clean_url starts with the website variable
            if clean_url.startswith(website):
                return clean_url
    return "No link found"

def extract_text_from_divs_with_selenium(url, youtube:bool):
    # Set up the Selenium WebDriver
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    options.headless = True  # Run in headless mode (without opening a browser window)

    # Fetch the webpage
    driver.get(url)
    
    # Wait for the necessary elements to load (adjust the time as needed)
    driver.implicitly_wait(10)  # Waits up to 10 seconds

    # Get the page source and close the browser
    page_source = driver.page_source
    driver.quit()

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find all divs with the specified class and extract the text
    if youtube:
        # Find all the search result links
        links = soup.find_all('a')
        
        # Extract and return the first relevant link
        for link in links:
            href = link.get('href')
            if href and href.startswith("/watch?v="):  # Check if 'href' starts with '/watch?v='
                full_url = f"https://www.youtube.com{href}"  # Construct the full URL
                return full_url  # Return the first matching URL
        return "No YouTube link found"
    else:
        extracted_texts = []
        divs = soup.find_all('div', class_="MuiBox-root css-165casq")
        for div in divs:
            lines = div.find_all('div', recursive=False)  # Only direct child divs
            for line in lines:
                extracted_texts.append(line.get_text(strip=True))
        
        return extracted_texts

def main() -> None:
    query = f"{singer} {song}".replace(' ', '+')
    url = f"https://www.google.com/search?q=site:{website_url}+{query}"
    
    # Capture the Google search result page for the targeted website

    # Send the HTTP request
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    lyrics_links = find_lyrics_link(website_url, singer, song)

    html_string =  f'Link to lyrics with song {song}:<br><a href="{lyrics_links}" target="_blank">Singer {singer} Song {song}</a>'
    st.markdown(html_string, unsafe_allow_html=True)
    
    # Having received a link to a website with lyrics to a song on it, we will make a function that will extract the lyrics from this link.

    lyrics_text = extract_text_from_divs_with_selenium(lyrics_links, False)

    html_string = f'<h2>Singer: {singer} </h2><br>'
    st.markdown(html_string, unsafe_allow_html=True)
    html_string = f'<h2>Song: {song}</h2><br><br>'
    st.markdown(html_string, unsafe_allow_html=True)
    
    for text in lyrics_text:
        html_string = f'<b><i>{text}</i></b>'
        st.markdown(html_string, unsafe_allow_html=True)

    # Format the query string for youtube search of content on the targeted website.

    url_youtube = f"https://www.youtube.com/results?search_query={query}"
        
    youtube_link = extract_text_from_divs_with_selenium(url_youtube, True)

    html_string = f'Link to video with song {song}:<br><a href="{youtube_link}" target="_blank">Singer {singer} Song {song}</a>'
    st.markdown(html_string, unsafe_allow_html=True)
    

# Format the query string for google search of content on the targeted website.
website_url = "https://lyrics.lyricfind.com"
singer = st.text_input('Enter Singer', 'Singer name')
song = st.text_input('Enter Song name', 'song name')

st.button("Search song now!", on_click=main)