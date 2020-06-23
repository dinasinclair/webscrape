"""
Misc functions to help debug/understand frontend status.
"""


def print_all_iframes(driver) -> None:
    """Prints all iframes in a current driver page source.
    Should not be in a class, should be a general tool"""
    print("all iframes: ")
    iframes = driver.find_elements_by_xpath("//iframe")
    print("found {} frames".format(len(iframes)))
    for frame in iframes:
        print(frame)
        print(frame.get_attribute('id'))
        print(frame.get_attribute('title'))


def print_all_ids_avail(driver) -> None:
    """
    Prints all named ids of elements in the self.driver page source.
    Should not be in a class, is a general tool (or at least, static)

    Returns:

    """
    print("all ids:")
    ids = driver.find_elements_by_xpath('//*[@id]')
    for ii in ids:
        # if 'apply' in ii.get_attribute('id'):
        print(ii.get_attribute('id'))


def print_all_aria_labels_avail(driver) -> None:
    """
    Prints all named ids of elements in the self.driver page source.
    Should not be in a class, is a general tool (or at least, static)

    Returns:

    """
    print("all ids:")
    ids = driver.find_elements_by_xpath('//*[@aria-label]')
    for ii in ids:
        # if 'apply' in ii.get_attribute('id'):
        print(ii.get_attribute('aria-label'))
