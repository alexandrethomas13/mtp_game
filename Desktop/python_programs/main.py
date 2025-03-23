import os
import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import time
from transformers import pipeline
import pytesseract
import cv2
import json

# Configuration
SUBJECTS = ['math', 'english', 'french', 'history', 'geography', 'qcc', 'music', 'pe']

class MozaikManager:
    def __init__(self):
        self.grades_cache = {}
        self.driver = None

    def analyze_image_for_text(self, image_path):
        """Analyze an image for text using Tesseract OCR."""
        img = cv2.imread(image_path)
        text = pytesseract.image_to_string(img)
        return text

    def login(self, email, password):
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # Enable for production
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        chromedriver_autoinstaller.install()

        try:
            self.driver = webdriver.Chrome(options=options)
            print("Browser initialized...")

            # Navigate to Mozaik portal
            self.driver.get("https://mozaikportail.ca/")
            print("Navigating to Mozaik login page...")

            # Click initial login button
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Se connecter"))
            ).click()
            print("Clicked 'Se connecter'")

            # Select email login method
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Adresse courriel')]"))
            ).click()
            print("Selected email login method")

            # Enter email and submit
            email_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="Email"], input[id="Email"]'))
            )
            email_field.send_keys(email)
            email_field.send_keys(Keys.RETURN)
            print(f"Submitted email: {email}")

            # Enter password and submit
            password_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
            print("Submitted password")

            # Verify successful login
            WebDriverWait(self.driver, 30).until(
                EC.url_contains("portail.mozaikc.com")
            )
            print("Login successful")

            # Add grade scraping logic here
            # ...

            self.driver.quit()
            return True

        except Exception as e:
            print(f"Login failed: {str(e)}")
            if self.driver:
                self.driver.save_screenshot("login_error.png")
                self.driver.quit()
            return False

class GradeBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

        self.mozaik = MozaikManager()
        self.ai_model = pipeline('text-generation', model='gpt2', device=0)

    def get_subject_grades(self, subject):
        return self.mozaik.grades_cache.get(subject, [])

    def calculate_average(self, grades):
        return sum(grades)/len(grades) if grades else 0

bot = GradeBot()

# Subject commands
@bot.command(name='math')
async def math_grades(ctx):
    grades = bot.get_subject_grades('math')
    await ctx.send(f"**Math Grades:**\n" + "\n".join(map(str, grades)) if grades else "No grades found")

@bot.command(name='english')
async def english_grades(ctx):
    grades = bot.get_subject_grades('english')
    await ctx.send(f"**English Grades:**\n" + "\n".join(map(str, grades)) if grades else "No grades found")

@bot.command(name='french')
async def french_grades(ctx):
    grades = bot.get_subject_grades('french')
    await ctx.send(f"**French Grades:**\n" + "\n".join(map(str, grades)) if grades else "No grades found")

@bot.command(name='history')
async def history_grades(ctx):
    grades = bot.get_subject_grades('history')
    await ctx.send(f"**History Grades:**\n" + "\n".join(map(str, grades)) if grades else "No grades found")

@bot.command(name='geography')
async def geography_grades(ctx):
    grades = bot.get_subject_grades('geography')
    await ctx.send(f"**Geography Grades:**\n" + "\n".join(map(str, grades)) if grades else "No grades found")

@bot.command(name='qcc')
async def qcc_grades(ctx):
    grades = bot.get_subject_grades('qcc')
    await ctx.send(f"**QCC Grades:**\n" + "\n".join(map(str, grades)) if grades else "No grades found")

@bot.command(name='music')
async def music_grades(ctx):
    grades = bot.get_subject_grades('music')
    await ctx.send(f"**Music Grades:**\n" + "\n".join(map(str, grades)) if grades else "No grades found")

@bot.command(name='pe')
async def pe_grades(ctx):
    grades = bot.get_subject_grades('pe')
    await ctx.send(f"**PE Grades:**\n" + "\n".join(map(str, grades)) if grades else "No grades found")

@bot.command()
async def login(ctx, email: str, password: str):
    """Login to Mozaik with email and password"""
    await ctx.message.delete()
    if bot.mozaik.login(email, password):
        await ctx.send("Login successful! 🎉")
    else:
        await ctx.send("Login failed ❌ Check credentials or try again later.")

@bot.command()
async def analyze(ctx, subject: str):
    grades = bot.get_subject_grades(subject.lower())
    if not grades:
        await ctx.send("No grades found for this subject")
        return

    prompt = f"""Analyze these {subject} grades: {grades}
    - Current average
    - Performance trend
    - Study recommendations"""

    analysis = bot.ai_model(prompt, max_length=200)[0]['generated_text']
    await ctx.send(f"**{subject.upper()} Analysis:**\n{analysis}")

@bot.command()
async def helpme(ctx):
    help_text = """
    **Available Commands:**
    !login [email] [password] - Connect to Mozaik
    ![subject] - Show grades for a subject
    !analyze [subject] - Get AI analysis of grades
    Subjects: """ + ", ".join(SUBJECTS)
    await ctx.send(help_text)

if __name__ == '__main__':
    from keep_alive import keep_alive
    keep_alive()
    bot.run(os.environ['DISCORD_TOKEN'])