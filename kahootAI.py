import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class KahootAIBot:
    def __init__(self, openrouter_api_key, game_pin, nickname):
        self.openrouter_api_key = openrouter_api_key
        self.game_pin = game_pin
        self.nickname = nickname
        self.driver = None
        self.wait = None
        self.setup_driver()
        
    def setup_driver(self):
        """Set up Chrome WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_window_size(1280, 800)  # Set a reasonable window size
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 10)
        
    def ask_ai(self, question, choices):
        """Send question to OpenRouter API"""
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        prompt = f"""
Question: {question}

Answer choices:
{chr(10).join([f"{i+1}. {choice}" for i, choice in enumerate(choices)])}

Choose the number of the correct answer (only a digit from 1 to {len(choices)}).
Reply with only the number, no explanations.
"""
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "google/gemma-3-12b-it:free",
            "messages": [
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 10,
            "temperature": 0.0
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=15)
            response.raise_for_status()
            
            result = response.json()
            answer_text = result['choices'][0]['message']['content'].strip()
            
            # Extract answer number
            import re
            numbers = re.findall(r'\d+', answer_text)
            if numbers:
                answer_num = int(numbers[0])
                if 1 <= answer_num <= len(choices):
                    return answer_num - 1  # Return 0-based index
            
            print(f"Could not extract a valid answer number from: {answer_text}")
            return 0  # Default to first option
            
        except Exception as e:
            print(f"Error contacting AI: {e}")
            return 0
    
    def join_game(self):
        """Join Kahoot game"""
        try:
            self.driver.get("https://kahoot.it/")
            
            # Enter PIN code
            pin_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-functional-selector='game-pin-input']"))
            )
            pin_input.send_keys(self.game_pin)
            
            # Click join button
            join_button = self.driver.find_element(By.CSS_SELECTOR, "[data-functional-selector='join-game-pin']")
            join_button.click()
            
            # Enter nickname
            nickname_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-functional-selector='username-input']"))
            )
            nickname_input.send_keys(self.nickname)
            
            # Confirm nickname
            confirm_button = self.driver.find_element(By.CSS_SELECTOR, "[data-functional-selector='join-button-username']")
            confirm_button.click()
            
            print(f"Successfully joined game {self.game_pin} as {self.nickname}")
            return True
            
        except Exception as e:
            print(f"Error joining game: {e}")
            return False
    
    def get_question_and_choices(self):
        """Get question text and answer choices"""
        try:
            # Check for question without waiting
            question_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-functional-selector='block-title']")
            if not question_elements:
                return None, []
            
            question_text = question_elements[0].text
            if not question_text.strip():
                return None, []
            
            # Get answer choices
            choices = []
            for i in range(4):  # Kahoot usually has up to 4 choices
                try:
                    choice_selector = f"[data-functional-selector='question-choice-text-{i}']"
                    choice_elements = self.driver.find_elements(By.CSS_SELECTOR, choice_selector)
                    if choice_elements and choice_elements[0].text.strip():
                        choices.append(choice_elements[0].text.strip())
                except Exception:
                    break
            
            if len(choices) == 0:
                return None, []
            
            return question_text, choices
            
        except Exception as e:
            print(f"Error getting question: {e}")
            return None, []
    
    def click_answer(self, answer_index):
        """Click the selected answer"""
        try:
            answer_selector = f"[data-functional-selector='answer-{answer_index}']"
            answer_button = self.driver.find_element(By.CSS_SELECTOR, answer_selector)
            answer_button.click()
            print(f"Clicked answer {answer_index + 1}")
            return True
        except Exception as e:
            print(f"Error clicking answer: {e}")
            return False
    
    def wait_for_next_question(self):
        """Wait for the next question"""
        time.sleep(3)  # Give time for next question to load
    
    def run_game(self):
        """Main game loop"""
        if not self.join_game():
            return
        
        print("Waiting for the game to start...")
        time.sleep(5)
        
        question_count = 0
        last_question = ""
        answered_questions = set()
        
        print("🔍 Looking for questions...")
        
        while True:
            try:
                # Get question and answer choices
                question, choices = self.get_question_and_choices()
                
                if not question or not choices:
                    print(".", end="", flush=True)  # Show progress
                    time.sleep(1)  # Wait 1 second before next attempt
                    continue
                
                # Check if we've already answered this question
                question_hash = hash(question + str(choices))
                if question_hash in answered_questions:
                    print(".", end="", flush=True)
                    time.sleep(1)
                    continue
                
                # New question found!
                if question != last_question:
                    question_count += 1
                    print(f"\n\n🎯 Question {question_count} found!")
                    print(f"📝 Question: {question}")
                    print(f"📋 Choices: {choices}")
                    
                    # Send to AI
                    print("🤖 Sending question to AI...")
                    ai_answer_index = self.ask_ai(question, choices)
                    
                    print(f"🎯 AI chose answer: {ai_answer_index + 1}. {choices[ai_answer_index]}")
                    
                    # Click the answer
                    if self.click_answer(ai_answer_index):
                        print("✅ Answer submitted!")
                        answered_questions.add(question_hash)
                        last_question = question
                    else:
                        print("❌ Failed to submit answer")
                    
                    # Wait a bit after submitting answer
                    time.sleep(2)
                else:
                    time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n\n⏹️ Game interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error in main loop: {e}")
                time.sleep(1)
                continue
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

def main():
    # Prompt user for OpenRouter API key
    OPENROUTER_API_KEY = input("Enter your OpenRouter API key: ").strip()
    
    print("🤖 Kahoot AI Bot is starting...")
    print("=" * 50)
    
    # Prompt user for game data
    GAME_PIN = input("Enter Kahoot game PIN: ").strip()
    NICKNAME = input("Enter your nickname: ").strip()
    
    if not OPENROUTER_API_KEY:
        print("❌ OpenRouter API key cannot be empty!")
        return
    if not GAME_PIN:
        print("❌ Game PIN cannot be empty!")
        return
    
    if not NICKNAME:
        print("❌ Nickname cannot be empty!")
        return
    
    print(f"\n✅ Game PIN: {GAME_PIN}")
    print(f"✅ Nickname: {NICKNAME}")
    print(f"✅ AI model: google/gemma-3-12b-it")
    print("\nStarting bot...")
    
    bot = KahootAIBot(OPENROUTER_API_KEY, GAME_PIN, NICKNAME)
    
    try:
        bot.run_game()
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        bot.close()
        print("Bot has stopped")

if __name__ == "__main__":
    main()
