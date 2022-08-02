def post_count_is_enough(driver, locator, num):
    elements = driver.find_elements(*locator)
    if len(elements) >= num:
        return elements
    else:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        return False
