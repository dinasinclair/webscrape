from constants import WAIT_SHORT
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import logging


def remove_all_popups(driver) -> None:
    """
    Tries to remove any possible popup encountered thus far by the webscraper.
    Args:
        driver:

    Returns:

    """
    driver.implicitly_wait(WAIT_SHORT)
    remove_legal_popup(driver)
    driver.implicitly_wait(WAIT_SHORT)
    remove_popover_popup(driver)
    driver.implicitly_wait(WAIT_SHORT)


def remove_legal_popup(driver) -> None:
    # This gets rid of the banner with id "icl-LegalConsentBanner-body"
    try:
        dismiss_legal_popup_button = driver.find_element_by_xpath("//button[text()='Dismiss']")
        dismiss_legal_popup_button.click()
        driver.implicitly_wait(WAIT_SHORT)
        logging.warning("closed legal consent popup!")
    except NoSuchElementException:
        logging.info("Didn't find a legal consent popup.")


def remove_popover_popup(driver) -> None:
    try:
        close_window_button = driver.find_element_by_id('popover-x')
        close_window_button.click()
        driver.implicitly_wait(WAIT_SHORT)
        logging.warning("closed popup via popover-x button!")
    except NoSuchElementException:
        logging.info("Didn't find a popover-x popup.")
        pass
