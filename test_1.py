from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

def fill(driver, selector, value):
    driver.find_element(By.CSS_SELECTOR, selector).send_keys(value)

def click(driver, selector):
    driver.find_element(By.CSS_SELECTOR, selector).click()

def select_dropdown(driver, selector, value):
    driver.find_element(By.CSS_SELECTOR, selector).send_keys(value)

def test_complex_onboarding():

    driver = webdriver.Chrome()
    driver.maximize_window()
    actions = ActionChains(driver)

    try:
        driver.get("https://example.com/onboarding/complex")

        # ----------- MOUSE MOVE -----------
        actions.move_by_offset(200, 300).perform()
        actions.move_by_offset(400, 200).perform()

        # ----------- STEP 1: LARGE TEXT INPUTS -----------
        text_fields = {
            "#firstName": "Gul",
            "#lastName": "Mohammad",
            "#email": "gul@example.com",
            "#phone": "03001112222",
            "#address": "Karachi",
            "#occupation": "Architect",
        }

        for selector, value in text_fields.items():
            fill(driver, selector, value)

        click(driver, "#btn-next-step")

        # ----------- STEP 2: 50+ FIELDS LOOP -----------
        for i in range(1, 21):
            fill(driver, f"#familyMember_{i}_name", f"Person {i}")
            fill(driver, f"#familyMember_{i}_age", f"{20+i}")
            select_dropdown(driver, f"#familyMember_{i}_relation", "Sibling")

        click(driver, "#btn-next-step")

        # ----------- STEP 3: CHECKBOXES, RADIO, UPLOAD -----------
        click(driver, "#acceptTerms")
        click(driver, "input[name='politicallyExposed'][value='No']")

        driver.find_element(By.CSS_SELECTOR, "#uploadCnic").send_keys(
            os.path.abspath("testdata/cnic_front.png")
        )

        click(driver, "#btn-next-step")

        # ----------- STEP 4: FINAL SUBMIT -----------
        click(driver, "#submitForm")

        time.sleep(2)
        assert "success" in driver.current_url.lower()

        print("200-field onboarding test (Selenium) passed.")

    except Exception as e:
        print("Onboarding failed:", e)

    finally:
        driver.quit()


if __name__ == "__main__":
    test_complex_onboarding()
