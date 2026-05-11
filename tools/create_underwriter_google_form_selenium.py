"""
Create a Google Form for SPARC liability-underwriter product validation.

This script uses Selenium against your logged-in Chrome session. Google Forms
does not support anonymous form creation, so the script pauses for manual login
if Chrome is not already authenticated.

Install once:
    python -m pip install selenium

Run:
    python tools/create_underwriter_google_form_selenium.py

Notes:
    - Keep Chrome visible while it runs.
    - If Google changes the Forms UI labels, the script will stop with a clear
      message instead of making partial edits silently.
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.common.exceptions import NoSuchElementException, TimeoutException
    from selenium.webdriver import ChromeOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Selenium is not installed. Run: python -m pip install selenium"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
CHROME_PROFILE = ROOT / ".chrome-profile" / "google-form-underwriter"
WAIT_SECONDS = int(os.environ.get("SPARC_FORM_WAIT_SECONDS", "300"))
ATTACH_TO_EXISTING_CHROME = "--attach" in sys.argv or os.environ.get("SPARC_ATTACH_CHROME") == "1"
NO_PAUSE = "--no-pause" in sys.argv or os.environ.get("SPARC_NO_PAUSE") == "1"
DEBUGGER_ADDRESS = os.environ.get("SPARC_CHROME_DEBUGGER", "127.0.0.1:9333")


DECISION_OPTIONS = [
    "Auto-recommend when SPARC trigger matches",
    "Recommend only with underwriter referral",
    "Add-on only, never rank as primary",
    "Do not recommend in SPARC",
    "Need more information before deciding",
]


@dataclass(frozen=True)
class Question:
    title: str
    help_text: str
    options: list[str]


QUESTIONS: list[Question] = [
    Question(
        "Cyber Liability: how should SPARC recommend this?",
        "Current use: Business Shield SME, Corporate Cover II, Business Edge, Enterprise Secure, IAR optional. Trigger signals include personal data, KYC, payments data, DPDP, CERT-In, SaaS, fintech, healthtech, edtech, and high data sensitivity.",
        DECISION_OPTIONS,
    ),
    Question(
        "Directors and Officers Liability: how should SPARC recommend this?",
        "Current use: Business Shield SME, Corporate Cover II, Industrial All Risk, Enterprise Secure. Trigger signals include institutional investors, Series A or later, board exposure, governance risk, and regulated sectors.",
        DECISION_OPTIONS,
    ),
    Question(
        "Professional Indemnity / Tech E&O: how should SPARC recommend this?",
        "Current use: Business Shield SME, Corporate Cover II, Industrial All Risk, Enterprise Secure. Trigger signals include SaaS, B2B services, fintech, healthtech, legaltech, consulting, implementation work, and enterprise contracts.",
        DECISION_OPTIONS,
    ),
    Question(
        "Public Liability: how should SPARC recommend this?",
        "Current use: MSME Suraksha, Bharat Sookshma, Corporate Cover II, Business Edge, Contractor All Risk, Enterprise Secure. Trigger signals include office, store, lab, factory, warehouse, events, site visits, and third-party premises exposure.",
        DECISION_OPTIONS,
    ),
    Question(
        "Product Liability: how should SPARC recommend this?",
        "Current use: MSME optional, Industrial All Risk optional, Enterprise Secure optional. Trigger signals include D2C, foodtech, hardware, pharma, medical devices, robotics, consumer products, and physical product control.",
        DECISION_OPTIONS,
    ),
    Question(
        "CGL / I-Elite Comprehensive General Liability: how should SPARC recommend this?",
        "Current use: component in Corporate Cover II and Enterprise Secure metadata. Trigger signals include broad third-party injury/property damage, enterprise contracts, export exposure, product-led operations, and higher liability limits.",
        DECISION_OPTIONS,
    ),
    Question(
        "Crime / Fidelity: how should SPARC recommend this?",
        "Current use: Business Shield SME, Corporate Cover II, Enterprise Secure. Trigger signals include employee access to money, finance teams, payment operations, fund handling, social engineering exposure, and internal fraud risk.",
        DECISION_OPTIONS,
    ),
    Question(
        "Employment Practices Liability: how should SPARC recommend this?",
        "Current use: Business Shield SME and Group Safeguard. Trigger signals include scaling headcount, POSH exposure, hiring/termination activity, gig labour, HR disputes, and workforce misclassification risk.",
        DECISION_OPTIONS,
    ),
    Question(
        "Employees Compensation / Employer Liability: how should SPARC recommend this?",
        "Current use: Group Safeguard, Corporate Cover II, Business Edge, Enterprise Secure. Trigger signals include factory, warehouse, delivery, field sales, gig workers, lab workers, and hazardous occupations.",
        DECISION_OPTIONS,
    ),
    Question(
        "Healthcare / Medical Professional Liability: how should SPARC recommend this?",
        "Current use: specialist product in catalogue, pricing, and risk appetite. Trigger signals include clinics, diagnostics, telemedicine, doctors, hospitals, medtech, patient care, and clinical negligence exposure.",
        DECISION_OPTIONS,
    ),
    Question(
        "Financial Services / Institutions PI: how should SPARC recommend this?",
        "Current use: specialist fintech liability product. Trigger signals include NBFC, lending, payment aggregator, PPI, wealthtech, insurtech, investment advice, regulated financial services, and RBI/SEBI/IRDAI exposure.",
        DECISION_OPTIONS,
    ),
    Question(
        "Payment / Card Protection: how should SPARC recommend this?",
        "Current use: specialist payment product. Trigger signals include card issuing, payment programme ownership, consumer payment protection, unauthorised transactions, skimming, counterfeit, and payment fraud.",
        DECISION_OPTIONS,
    ),
    Question(
        "Product Recall / Contamination: how should SPARC recommend this?",
        "Current use: specialist product in catalogue, pricing, and risk appetite. Trigger signals include foodtech, FMCG, pharma, nutraceuticals, cosmetics, hardware, batch manufacturing, FSSAI/CDSCO, and recall exposure.",
        DECISION_OPTIONS,
    ),
    Question(
        "Drone RPAS: how should SPARC recommend this?",
        "Current use: mandatory/specialist route for commercial drone profiles. Trigger signals include drones/UAV equipment, DGCA/drone operations, drone logistics, agritech drones, surveying, and robotics.",
        DECISION_OPTIONS,
    ),
    Question(
        "Surety / Contract Performance: how should SPARC recommend this?",
        "Current use: Contractor All Risk optional component and specialist product. Trigger signals include tenders, bid bonds, performance bonds, EPC, solar projects, government contracts, and project guarantees.",
        DECISION_OPTIONS,
    ),
    Question(
        "Entertainment Production Package: how should SPARC recommend this?",
        "Current use: specialist event/production product. Trigger signals include film production, ad production, events, creator economy, production equipment, venues, cast, and abandonment exposure.",
        DECISION_OPTIONS,
    ),
    Question(
        "What should SPARC do when product fit is high but underwriting appetite is bad?",
        "This determines the app behaviour when the recommendation logic finds exposure but risk_appetite.py says the sector/product pairing is bad.",
        [
            "Show product but force underwriter referral",
            "Hide product from RM output",
            "Show as excluded with reason",
            "Allow RM to override",
            "Need more information before deciding",
        ],
    ),
    Question(
        "What should SPARC prioritize when ranking bundles?",
        "Current scoring blends coverage fit, exposure fit, regulatory fit, and commercial fit. TAM should not override underwriting correctness.",
        [
            "Coverage correctness first",
            "Regulatory trigger correctness first",
            "Premium adequacy first",
            "RM sales usefulness first",
            "Need more information before deciding",
        ],
    ),
]


def build_driver() -> webdriver.Chrome:
    if ATTACH_TO_EXISTING_CHROME:
        options = ChromeOptions()
        options.add_experimental_option("debuggerAddress", DEBUGGER_ADDRESS)
        return webdriver.Chrome(options=options)

    CHROME_PROFILE.mkdir(parents=True, exist_ok=True)
    options = ChromeOptions()
    options.add_argument(f"--user-data-dir={CHROME_PROFILE}")
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)
    return webdriver.Chrome(options=options)


def wait_for_form_editor(driver: webdriver.Chrome) -> None:
    wait = WebDriverWait(driver, WAIT_SECONDS)
    wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//*[@role='textbox' and (@aria-label='Form title' or @aria-label='Untitled form')]",
            )
        )
    )


def find_first(driver: webdriver.Chrome, xpaths: list[str]):
    for xpath in xpaths:
        matches = driver.find_elements(By.XPATH, xpath)
        if matches:
            return matches[0]
    raise NoSuchElementException("No element matched any candidate XPath.")


def clear_and_type(element, text: str) -> None:
    element.click()
    element.send_keys(Keys.CONTROL, "a")
    element.send_keys(text)


def set_form_title(driver: webdriver.Chrome) -> None:
    title = find_first(
        driver,
        [
            "//*[@role='textbox' and @aria-label='Form title']",
            "//*[@role='textbox' and @aria-label='Untitled form']",
            "(//*[@role='textbox'])[1]",
        ],
    )
    clear_and_type(title, "SPARC Liability Product Recommendation Review")

    description = find_first(
        driver,
        [
            "//*[@role='textbox' and contains(@aria-label, 'Form description')]",
            "(//*[@role='textbox'])[2]",
        ],
    )
    clear_and_type(
        description,
        "Please classify each liability product for the SPARC RM recommender. "
        "Choose the easiest answer that reflects underwriting appetite. "
        "Use 'Recommend only with underwriter referral' when an RM should not present "
        "the product without UW review.",
    )


def add_question_shell(driver: webdriver.Chrome) -> None:
    add_buttons = driver.find_elements(By.XPATH, "//*[@aria-label='Add question']")
    if not add_buttons:
        raise NoSuchElementException("Could not find the Google Forms Add question button.")
    add_buttons[0].click()
    time.sleep(0.7)


def active_question_title(driver: webdriver.Chrome):
    candidates = driver.find_elements(
        By.XPATH,
        "//*[@role='textbox' and (contains(@aria-label, 'Question') or contains(@aria-label, 'question'))]",
    )
    if candidates:
        return candidates[-1]
    textboxes = driver.find_elements(By.XPATH, "//*[@role='textbox']")
    if len(textboxes) < 3:
        raise NoSuchElementException("Could not find the question title textbox.")
    return textboxes[-1]


def active_option_boxes(driver: webdriver.Chrome):
    return driver.find_elements(
        By.XPATH,
        "//*[@role='textbox' and (contains(@aria-label, 'Option') or contains(@aria-label, 'option'))]",
    )


def set_question_description(driver: webdriver.Chrome, text: str) -> None:
    more = driver.find_elements(By.XPATH, "//*[@aria-label='More']")
    if more:
        more[-1].click()
        time.sleep(0.2)
        desc_items = driver.find_elements(By.XPATH, "//*[contains(text(), 'Description')]")
        if desc_items:
            desc_items[-1].click()
            time.sleep(0.3)

    desc_boxes = driver.find_elements(
        By.XPATH,
        "//*[@role='textbox' and (contains(@aria-label, 'Description') or contains(@aria-label, 'description'))]",
    )
    if desc_boxes:
        clear_and_type(desc_boxes[-1], text)


def fill_multiple_choice_question(driver: webdriver.Chrome, question: Question) -> None:
    title = active_question_title(driver)
    clear_and_type(title, question.title)
    time.sleep(0.2)
    set_question_description(driver, question.help_text)

    option_boxes = active_option_boxes(driver)
    if not option_boxes:
        raise NoSuchElementException("Could not find an option textbox for the active question.")

    option_boxes[-1].click()
    for index, option in enumerate(question.options):
        if index == 0:
            clear_and_type(option_boxes[-1], option)
        else:
            option_boxes = active_option_boxes(driver)
            option_boxes[-1].send_keys(Keys.ENTER)
            time.sleep(0.15)
            option_boxes = active_option_boxes(driver)
            clear_and_type(option_boxes[-1], option)


def main() -> None:
    driver = build_driver()
    driver.get("https://docs.google.com/forms/u/0/create")
    if ATTACH_TO_EXISTING_CHROME:
        print(f"Attached to existing Chrome at {DEBUGGER_ADDRESS}.")
    else:
        print("Chrome opened. If Google asks you to sign in, complete login in the browser.")
        print("If Google says the browser may not be secure, close this run and use:")
        print("    powershell -ExecutionPolicy Bypass -File tools/launch_google_forms_chrome.ps1")
        print("    python tools/create_underwriter_google_form_selenium.py --attach")
    if not NO_PAUSE:
        input("Press Enter here after the blank Google Form editor is visible...")
    else:
        print(f"Waiting up to {WAIT_SECONDS} seconds for the blank Google Form editor...")

    try:
        wait_for_form_editor(driver)
        set_form_title(driver)

        fill_multiple_choice_question(driver, QUESTIONS[0])
        for question in QUESTIONS[1:]:
            add_question_shell(driver)
            fill_multiple_choice_question(driver, question)

        print("\nDone. Review the form in Chrome, then click Send when ready.")
        print("Chrome profile used:", CHROME_PROFILE)
    except TimeoutException as exc:
        raise SystemExit("Timed out waiting for the Google Forms editor.") from exc
    except NoSuchElementException as exc:
        raise SystemExit(
            f"Google Forms UI element not found: {exc}\n"
            "The page may not be fully loaded, or Google may have changed the editor labels."
        ) from exc


if __name__ == "__main__":
    main()
