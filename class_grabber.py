from selenium import webdriver
import time, json, re





# CHANGE PATH TO CHROME DRIVER


DRIVER_PATH = "/home/lorn/Desktop/plan-parser/driver/chromedriver"

# ----------------------------------------------
# DO not modify anything after this part
# ----------------------------------------------


OUTPUT = {}

start = time.perf_counter()

driver = webdriver.Chrome(DRIVER_PATH)
driver.get("https://plany.ath.bielsko.pl/left_menu.php")


def do_expand(l):
    for case in l:
        driver.execute_script('arguments[0].click()', case)
        time.sleep(0.4)


to_check = []

main_tree = driver.find_element_by_class_name("main_tree")
items = main_tree.find_elements_by_tag_name("li")
for item in items:
    i = item.get_attribute("id")
    print(i, item.text)
    to_check.append((i, item.text))

time.sleep(1)

for idx, name in to_check:
    driver.refresh()

    CURRENT = {}

    time.sleep(1.5)
    category = driver.find_element_by_id(idx)
    driver.execute_script('arguments[0].click()', category.find_element_by_xpath("a"))
    time.sleep(1.5)

    expand = True
    while expand:
        l = driver.find_elements_by_xpath("//img[@src='images/plus.gif']")
        if len(l) <= 0:
            expand = False
        do_expand(l)

    time.sleep(5)

    for data in driver.find_elements_by_xpath("//img[@src='images/leafstudents.gif']/../a"):
        i = re.findall(r'id=\d+', data.get_attribute("href"))[0][3::]
        print(data.text, i)
        CURRENT.update({str(data.text): int(i)})
    OUTPUT.update({str(name): CURRENT})

    time.sleep(5)

with open('data', "w+", encoding="UTF-8") as f:
    f.write(json.dumps(OUTPUT, ensure_ascii=True, indent=2))

end = time.perf_counter()

driver.quit()

print("TIME END - START = ", end - start)
