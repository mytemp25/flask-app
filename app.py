from flask import Flask, request, jsonify
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import uuid
import secrets
import string
app = Flask(__name__)
def generate_username():
    return f"user_{uuid.uuid4().hex[:8]}"  # Short unique username

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + "@#$"
    return ''.join(secrets.choice(characters) for _ in range(length))


def init_driver():
    """Initialize Selenium WebDriver with headless Chrome."""
    options = uc.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)
    return driver

driver=None

def getEmail():
    url = "https://tempail.com/en/"
    try:
        global driver
        driver= init_driver()
        flag=0
        while(flag<3):
            try:
                driver.get(url)
                time.sleep(15)
                input=driver.find_element(By.ID,"eposta_adres")
                email=input.get_attribute('value')
                if email==None:
                    raise Exception()
                else:
                    return {"status":"found","email":email}
            except:
                flag=flag+1
        return {"status":"not found","error":"max tried"}
    except Exception as e:
        print(e)
        return {"status":"not found","error":"server error"}
    

def getCode():
    try:
        flag=0
        while(flag<3):
            try:
                mail_item= WebDriverWait(driver, 30).until(
                         EC.presence_of_element_located((By.CLASS_NAME, "mail"))
                         )
                link=mail_item.find_element(By.TAG_NAME,'a').get_attribute("href")
                print(link)
                if link==None:
                    raise Exception()
                else:
                    break
            except:
                flag=flag+1
                time.sleep(3)

        flag=0
        while(flag<3):
            try:
                driver.get(link)
                frame=WebDriverWait(driver, 10).until(
                         EC.presence_of_element_located((By.ID, "iframe"))
                         )
                driver.switch_to.frame(frame)
                
                code = WebDriverWait(driver, 10).until(
                 EC.presence_of_element_located((By.XPATH, "//p/strong"))
                 ).text
                print(code)
                if code==None:
                    raise Exception()
                else:
                    return {"status":"found","code":code}
            except:
                flag=flag+1

        return {"status":"not found","error":"max tried"}
    except Exception as e:
        print(e)
        return {"status":"not found","error":"server error"}

@app.route('/signup',methods=['GET'])
def signup():
    print("start")
    try:
        driver1= init_driver()
        email_data=getEmail()
        if email_data['status']!="found":
            print(email_data)
            return jsonify(email_data)
        username=generate_username()
        password=generate_password()
        email=email_data["email"]
        print(email,username,password)
        flag=0
        while(flag<3):
            try:
                driver1.get("https://sunoapi.org/signup")
                form_inputs = WebDriverWait(driver1, 15).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//form/div/div/div/input"))
                 )

                form_inputs[0].send_keys(email)
                driver1.find_element(By.XPATH, '//form/div/div/div/button').click()
                print("waiting for code")
                code_data=getCode()
                print(code_data)
                if code_data["status"]!="found":
                     raise Exception()
                code = code_data["code"]
                form_inputs[1].send_keys(code)
                form_inputs[2].send_keys(username)
                form_inputs[3].send_keys(password)
                form_inputs[4].send_keys(password)
                
                driver1.find_element(By.XPATH, '//form/button').click()
                WebDriverWait(driver1, 15).until(
                 EC.presence_of_element_located((By.XPATH, '//nav/a[3]'))
                 ).click()
                api_key = WebDriverWait(driver1, 15).until(
                     EC.presence_of_element_located((By.CSS_SELECTOR, 'div.inline-flex.w-full.items-center.h-full.box-border > input'))
                        ).get_attribute("value")
                print(api_key)
                return jsonify({"email": email, "username": username, "password": password, "api_key": api_key})
            except Exception as e:
                print(e)
                flag=flag+1
    except Exception as e:
        print(e)
        return jsonify("error")
    finally:
        driver.quit()
        driver1.quit()
@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    driver = init_driver()
    try:
        driver.get("https://sunoapi.org/login")
        
        form_inputs = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, "//form/div/div/div/input"))
        )

        form_inputs[0].send_keys(email)
        form_inputs[1].send_keys(password)
        driver.find_element(By.XPATH, '//form/button').click()

        # Get API Key
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//nav/a[3]'))
        ).click()

        api_key = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.inline-flex.w-full.items-center.h-full.box-border > input'))
        ).get_attribute("value")

        return jsonify({"api_key": api_key})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

    finally:
        driver.quit()  

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
