import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Optional, Dict
import random

class SnapchatAutomation:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.setup_driver()
    
    def setup_driver(self):
        """Initialize the web driver"""
        chrome_options = Options()
        
        # Add useful Chrome options
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_experimental_option("detach", True)
        
        # Add user agent to appear more like a regular browser
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)
            
            # Navigate to Snapchat web
            print("Setting up Snapchat Web...")
            self.driver.get("https://web.snapchat.com/")
            
            # Wait for user to log in
            print("\n" + "="*50)
            print("SETUP INSTRUCTIONS:")
            print("1. Log in to your Snapchat account in the browser")
            print("2. Navigate to the main chat/friends page")
            print("3. Press Enter in this console when ready...")
            print("="*50 + "\n")
            
            input("Press Enter when you're logged in and ready...")
            
            # Verify we're logged in by looking for common elements
            self._verify_login()
            
        except Exception as e:
            print(f"Error setting up driver: {e}")
            raise
    
    def _verify_login(self):
        """Verify that we're successfully logged into Snapchat"""
        try:
            # Look for elements that indicate we're logged in
            login_indicators = [
                "[data-testid='chat-input']",
                ".friends-list",
                "[aria-label='Search']",
                "input[placeholder*='Search']"
            ]
            
            found = False
            for indicator in login_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                    if element.is_displayed():
                        found = True
                        break
                except:
                    continue
            
            if found:
                print("✅ Successfully detected Snapchat interface!")
            else:
                print("⚠️  Could not verify login. Please ensure you're on the main Snapchat page.")
                
        except Exception as e:
            print(f"Login verification error: {e}")
    
    def get_user_score(self, username: str) -> Optional[Dict]:
        """Get the current score and snap status for a user"""
        try:
            print(f"Getting score for: {username}")
            
            # Search for the user
            if not self._search_user(username):
                print(f"Could not search for user: {username}")
                return None
            
            # Navigate to user profile
            if not self._open_user_profile(username):
                print(f"Could not open profile for: {username}")
                return None
            
            # Extract score
            score = self._extract_score()
            print(f"Extracted score: {score}")
            
            # Check for new snaps
            has_new_snap = self._check_new_snap()
            print(f"Has new snap: {has_new_snap}")
            
            # Go back to main page for next search
            self._go_back_to_main()
            
            if score is not None:
                return {
                    'score': score,
                    'has_new_snap': has_new_snap,
                    'timestamp': time.time()
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting score for {username}: {e}")
            # Try to go back to main page even if there was an error
            try:
                self._go_back_to_main()
            except:
                pass
            return None
    
    def _search_user(self, username: str) -> bool:
        """Search for a user in Snapchat"""
        try:
            # Look for search box with multiple strategies
            search_selectors = [
                "input[placeholder*='Search']",
                "input[placeholder*='search']",
                "input[data-testid='search-input']",
                ".search-input",
                "[aria-label='Search']",
                "[aria-label*='search']",
                "input[type='text']"
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            search_box = element
                            break
                    if search_box:
                        break
                except:
                    continue
            
            if not search_box:
                print("Could not find search box")
                return False
            
            # Clear any existing text and enter username
            search_box.click()
            time.sleep(1)
            search_box.clear()
            time.sleep(0.5)
            
            # Type username slowly to mimic human behavior
            for char in username:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            # Wait for search results
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"Error searching for user: {e}")
            return False
    
    def _open_user_profile(self, username: str) -> bool:
        """Click on user profile from search results"""
        try:
            # Wait a bit for search results to load
            time.sleep(1)
            
            # Strategy 1: Look for exact username matches
            possible_selectors = [
                f"[data-testid*='{username}']",
                f"[title*='{username}']",
                f"[aria-label*='{username}']"
            ]
            
            for selector in possible_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            time.sleep(3)
                            return True
                except:
                    continue
            
            # Strategy 2: Look for text content containing username
            try:
                # Look for any clickable element containing the username
                xpath_queries = [
                    f"//div[contains(text(), '{username}')]",
                    f"//span[contains(text(), '{username}')]",
                    f"//p[contains(text(), '{username}')]",
                    f"//*[contains(@class, 'friend') and contains(text(), '{username}')]",
                    f"//*[contains(@class, 'user') and contains(text(), '{username}')]"
                ]
                
                for xpath in xpath_queries:
                    try:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        for element in elements:
                            if element.is_displayed() and username.lower() in element.text.lower():
                                # Look for clickable parent
                                clickable = self._find_clickable_parent(element)
                                if clickable:
                                    clickable.click()
                                    time.sleep(3)
                                    return True
                    except:
                        continue
                        
            except Exception as e:
                print(f"XPath search error: {e}")
            
            # Strategy 3: Try clicking first search result if it looks like a user
            try:
                result_selectors = [
                    "[data-testid*='friend']",
                    ".friend-item",
                    ".search-result",
                    ".user-item"
                ]
                
                for selector in result_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements and elements[0].is_displayed():
                            elements[0].click()
                            time.sleep(3)
                            return True
                    except:
                        continue
                        
            except Exception as e:
                print(f"First result click error: {e}")
            
            print(f"Could not find and click on user: {username}")
            return False
            
        except Exception as e:
            print(f"Error opening user profile: {e}")
            return False
    
    def _find_clickable_parent(self, element):
        """Find a clickable parent element"""
        current = element
        for _ in range(5):  # Go up max 5 levels
            try:
                current = current.find_element(By.XPATH, "..")
                if current.tag_name in ['a', 'button'] or 'click' in current.get_attribute('onclick') or '':
                    return current
                # Check if element has click handlers
                if current.get_attribute('onclick') or 'cursor: pointer' in current.get_attribute('style') or '':
                    return current
            except:
                break
        return element
    
    def _extract_score(self) -> Optional[int]:
        """Extract the Snapchat score from the current page"""
        try:
            # Wait for page to load
            time.sleep(2)
            
            # Strategy 1: Look for common score selectors
            score_selectors = [
                "[data-testid*='score']",
                ".snap-score",
                "[aria-label*='score']",
                ".profile-score",
                "*[class*='score']",
                "*[id*='score']"
            ]
            
            for selector in score_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            score_text = element.text
                            score = self._parse_score(score_text)
                            if score is not None:
                                return score
                except:
                    continue
            
            # Strategy 2: Look for patterns in all visible text
            try:
                # Get all text elements that might contain scores
                text_elements = self.driver.find_elements(By.XPATH, "//*[text()]")
                
                for element in text_elements:
                    try:
                        if element.is_displayed():
                            text = element.text.strip()
                            score = self._parse_score_from_text(text)
                            if score is not None:
                                return score
                    except:
                        continue
                        
            except Exception as e:
                print(f"Text parsing error: {e}")
            
            # Strategy 3: Look in page source for score patterns
            try:
                page_source = self.driver.page_source
                score = self._parse_score_from_html(page_source)
                if score is not None:
                    return score
            except:
                pass
            
            print("Could not extract score from page")
            return None
            
        except Exception as e:
            print(f"Error extracting score: {e}")
            return None
    
    def _parse_score(self, text: str) -> Optional[int]:
        """Parse score from text"""
        if not text:
            return None
            
        try:
            # Remove common formatting and extract numbers
            clean_text = re.sub(r'[^\d]', '', text)
            if clean_text and len(clean_text) <= 7:  # Reasonable score limit
                score = int(clean_text)
                if 0 <= score <= 10000000:  # Sanity check
                    return score
        except:
            pass
        return None
    
    def _parse_score_from_text(self, text: str) -> Optional[int]:
        """Parse score from general text using patterns"""
        if not text or len(text) > 100:  # Skip very long text
            return None
        
        # Patterns that might indicate a score
        score_patterns = [
            r'(\d{1,7})\s*(?:snap\s*)?score',
            r'score[:\s]*(\d{1,7})',
            r'(\d{1,7})\s*points?',
            r'^(\d{4,7})$',  # Just a number in reasonable range
        ]
        
        for pattern in score_patterns:
            try:
                match = re.search(pattern, text.lower())
                if match:
                    score = int(match.group(1))
                    if 100 <= score <= 10000000:  # Reasonable score range
                        return score
            except:
                continue
        
        return None
    
    def _parse_score_from_html(self, html: str) -> Optional[int]:
        """Parse score from HTML source"""
        try:
            # Look for score in data attributes or JSON
            patterns = [
                r'"score"[:\s]*(\d{1,7})',
                r'data-score["\s]*=["\s]*(\d{1,7})',
                r'snapScore["\s]*:["\s]*(\d{1,7})',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for match in matches:
                    try:
                        score = int(match)
                        if 100 <= score <= 10000000:
                            return score
                    except:
                        continue
        except:
            pass
        
        return None
    
    def _check_new_snap(self) -> bool:
        """Check if there's a new snap indicator"""
        try:
            # Look for new snap indicators
            new_snap_selectors = [
                ".new-snap-indicator",
                "[data-testid*='new-snap']",
                ".unread-indicator",
                ".notification-dot",
                "*[class*='unread']",
                "*[class*='new']",
                "*[class*='notification']"
            ]
            
            for selector in new_snap_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            return True
                except:
                    continue
            
            # Look for visual indicators (red dots, etc.)
            try:
                # Look for elements with red background or notification styling
                indicators = self.driver.find_elements(By.XPATH, 
                    "//*[contains(@style, 'red') or contains(@class, 'red') or contains(@class, 'dot')]")
                for indicator in indicators:
                    if indicator.is_displayed() and indicator.size['width'] > 0:
                        return True
            except:
                pass
            
            return False
            
        except Exception as e:
            print(f"Error checking new snap: {e}")
            return False
    
    def _go_back_to_main(self):
        """Navigate back to main page for next search"""
        try:
            # Try pressing escape key to close any dialogs
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            time.sleep(1)
            
            # Try to navigate to main page
            main_selectors = [
                "[data-testid='home']",
                ".home-button",
                "[aria-label='Home']",
                "a[href*='chat']"
            ]
            
            for selector in main_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        element.click()
                        time.sleep(1)
                        return
                except:
                    continue
            
            # If no home button found, try refreshing the page
            current_url = self.driver.current_url
            if 'web.snapchat.com' in current_url:
                self.driver.get("https://web.snapchat.com/")
                time.sleep(3)
                
        except Exception as e:
            print(f"Error going back to main: {e}")
    
    def close(self):
        """Close the browser"""
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass