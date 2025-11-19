
from playwright.sync_api import sync_playwright
import time

def fill_text_fields(page, fields):
    for selector, value in fields.items():
        page.fill(selector, value)

def select_dropdowns(page, dropdowns):
    for selector, option in dropdowns.items():
        page.select_option(selector, option)

def click_elements(page, click_list):
    for selector in click_list:
        page.click(selector)

def upload_files(page, files):
    for selector, file_path in files.items():
        page.set_input_files(selector, file_path)

def test_complex_onboarding():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://example.com/onboarding/complex")

        # Move mouse around (simulating real user)
        page.mouse.move(200, 200)
        page.mouse.move(500, 500)

        # ---------- STEP 1: BASIC TEXT INPUTS ----------
        text_fields_step1 = {
            "#firstName": "Gul",
            "#middleName": "Mohammad",
            "#lastName": "Khan",
            "#fatherName": "Abdul Latif",
            "#motherName": "Gulshan",
            "#email": "gul@example.com",
            "#phone": "03001234567",
            "#altPhone": "03111234567",
            "#dob": "1990-05-15",
            "#nationality": "Pakistani",
            "#occupation": "Software Architect",
            "#companyName": "Auton8 Pvt Ltd",
            "#annualIncome": "5000000",
        }
        fill_text_fields(page, text_fields_step1)
        page.click("#next-step")

        # ---------- STEP 2: ADDRESS INFO ----------
        text_fields_step2 = {
            "#houseNumber": "A-22",
            "#streetName": "Shahrah-e-Faisal",
            "#area": "Gulshan",
            "#city": "Karachi",
            "#province": "Sindh",
            "#zip": "75500",
            "#country": "Pakistan",
        }
        fill_text_fields(page, text_fields_step2)

        dropdowns_step2 = {
            "#addressType": "permanent",
            "#residenceStatus": "owned",
        }
        select_dropdowns(page, dropdowns_step2)

        page.click("#next-step")

        # ---------- STEP 3: FINANCIAL DETAILS ----------
        text_fields_step3 = {
            "#bankName": "UBL",
            "#iban": "PK36UNIL0001234567891002",
            "#accountType": "Current",
            "#monthlyExpenses": "250000",
            "#monthlySavings": "100000",
        }
        fill_text_fields(page, text_fields_step3)

        dropdowns_step3 = {
            "#salarySource": "job",
            "#riskProfile": "medium",
        }
        select_dropdowns(page, dropdowns_step3)

        page.click("#next-step")

        # ---------- STEP 4: MULTIPLE REPEATED FIELDS (EXAMPLE LOOP) ----------
        # 10 employment history blocks (scalable to 200+ fields)
        for i in range(1, 6):
            page.fill(f"#employment_{i}_company", f"Company {i}")
            page.fill(f"#employment_{i}_designation", f"Senior Role {i}")
            page.fill(f"#employment_{i}_years", f"{i}")
            page.select_option(f"#employment_{i}_type", "fulltime")

        page.click("#next-step")

        # ---------- STEP 5: UPLOAD MANY DOCUMENTS ----------
        file_uploads = {
            "#cnicFront": "testdata/cnic_front.png",
            "#cnicBack": "testdata/cnic_back.png",
            "#salarySlip": "testdata/salary_slip.pdf",
            "#utilityBill": "testdata/bill.pdf",
            "#profilePhoto": "testdata/selfie.jpg",
        }
        upload_files(page, file_uploads)
        page.click("#next-step")

        # ---------- STEP 6: CHECKBOXES, RADIO BUTTONS, HOVERS ----------
        page.hover("#riskDisclosureInfo")
        click_elements(page, [
            "#agreeTerms",
            "#agreePrivacy",
            "input[name='politicallyExposed'][value='no']",
            "input[name='taxResident'][value='yes']",
        ])

        page.click("#submitApplication")

        # Wait for success
        page.wait_for_url("**/success")
        assert "success" in page.url.lower()

        print("200-field onboarding test (Playwright) passed.")
        browser.close()


if __name__ == "__main__":
    test_complex_onboarding()
