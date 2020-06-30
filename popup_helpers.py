from constants import WAIT_SHORT
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException


def remove_legal_popup(driver) -> None:
    # This gets rid of the banner with id "icl-LegalConsentBanner-body"
    try:
        dismiss_legal_popup_button = driver.find_element_by_xpath("//button[text()='Dismiss']")
        dismiss_legal_popup_button.click()
        driver.implicitly_wait(WAIT_SHORT)
        print("closed legal consent popup!")
    except NoSuchElementException:
        print("Didn't find a legal consent popup.")
        pass


def remove_popover_popup(driver) -> None:
    try:
        close_window_button = driver.find_element_by_id('popover-x')
        close_window_button.click()
        driver.implicitly_wait(WAIT_SHORT)
        print("closed popup via popover-x button!")
    except NoSuchElementException:
        print("Didn't find a popover-x popup.")
        pass
