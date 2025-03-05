import platform
import time
import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from deep_translator import GoogleTranslator
from Crawler import Crawl  # Your provided Crawler.py

# Read lines from titles.txt
with open('titles.txt', 'r', encoding='utf-8') as file:
    titles = [line.strip() for line in file]

if not titles:
    raise ValueError("The file must contain at least one line.")

# Use webdriver_manager to automatically download and set up ChromeDriver
driver_path = ChromeDriverManager().install()
baseUrl = 'https://askoptimo.com/tools/blog-post-generator'

try:
    # Initialize Crawl with the dynamically managed ChromeDriver path
    document = Crawl(baseUrl, executable_path=driver_path)
except Exception as e:
    print(f"Failed to initialize Crawler: {e}")
    exit(1)

document.set_link(baseUrl, 'tools')

document.click_element('x_path', '//*[@id="__next"]/div[2]/div/div/div[2]/div/div/button')
document.waiting('email')
document.fill_input('id', 'email', 'tesahik273@tiervio.com')
document.fill_input('id', 'password', '1234567890')
document.click_element('x_path', '//*[@id="__next"]/div[7]/div/div/form/div[2]/div[3]/button')
time.sleep(2)

# Open three files to save the results
with open('persian_only.txt', 'w', encoding='utf-8') as f_persian, \
        open('english_only.txt', 'w', encoding='utf-8') as f_english, \
        open('both_translations.txt', 'w', encoding='utf-8') as f_both:
    batch_size = 10
    total_titles = len(titles)
    num_batches = (total_titles + batch_size - 1) // batch_size  # Calculate the number of batches

    for batch_index in range(num_batches):
        start_index = batch_index * batch_size
        end_index = min(start_index + batch_size, total_titles)
        current_titles = titles[start_index:end_index]

        # Open tabs and perform actions for the current batch
        for tab_index, title in enumerate(current_titles):
            if tab_index == 0:
                # Use the initial tab for the first title
                document.set_link(baseUrl, 'tools')
            else:
                # Open a new tab for subsequent titles
                document.open_new_tab()
                document.switch_to_tab(tab_index)
                document.set_link(baseUrl, 'tools')

            document.fill_input('x_path', '//*[@id="tools"]/section/div/div[3]/form/div/textarea', title)
            document.click_element('x_path', '//*[@id="tools"]/section/div/div[3]/form/button')

        # Wait for results to be generated
        time.sleep(10)

        # Process each tab in the current batch
        for tab_index in range(len(current_titles)):
            document.switch_to_tab(tab_index)
            document.waiting('result')
            try:
                text_content = document.get_content("x_path", '//*[@id="result"]/p', content_type="text")

                if text_content is None:
                    raise ValueError("text_content is None")

                if not text_content.strip():
                    raise ValueError("Empty content")

                translated_fa = GoogleTranslator(source='auto', target='fa').translate(text_content)
                translated_en = GoogleTranslator(source='auto', target='en').translate(text_content)
                translated_title = GoogleTranslator(source='auto', target='en').translate(current_titles[tab_index])

                # Write to Persian-only file
                f_persian.write(f"{current_titles[tab_index]}:\n{translated_fa}\n\n")
                f_persian.write("=" * 50 + "\n\n")

                # Write to English-only file
                f_english.write(f"{translated_title}:\n{translated_en}\n\n")
                f_english.write("=" * 50 + "\n\n")

                # Write to both translations file
                f_both.write(f"{translated_title}:\n{translated_en}\n\n")
                f_both.write(f"{current_titles[tab_index]}:\n{translated_fa}\n\n")
                f_both.write("=" * 50 + "\n\n")

            except Exception as e:
                print(f"Skipping content for Batch {batch_index + 1}, Tab {tab_index + 1} due to error: {e}")

        # Close the tabs of the current batch before starting the next batch
        document.open_new_tab()
        for tab_index in range(len(current_titles)):
            try:
                time.sleep(1)
                document.switch_to_tab(0)
                document.driver.close()
            except selenium.common.exceptions.NoSuchWindowException:
                # If the window is already closed, continue to the next one
                print(f"Tab {tab_index} is already closed.")
                continue

        # Switch back to the first tab before opening new ones for the next batch
        if batch_index != num_batches - 1:
            document.switch_to_tab(0)

print("Translation and saving completed.")

input('Press Enter to continue...')