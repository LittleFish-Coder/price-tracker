import smtplib
import json
import requests
import schedule
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import time


def send_email(email_from, password, to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = email_from
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    print(msg)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_from, password)
        server.sendmail(email_from, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


def get_info():
    with open("config.json", "r") as file:
        config = json.load(file)

    email_from = config["email_from"]
    password = config["password"]
    email_to = config["email_to"]

    return email_from, password, email_to


def track_price(url: str):

    # request
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    price = soup.find("span", {"class": "a-price-whole"}).get_text()
    print(f"Time: {time.ctime()}, Price: {price}")

    try:
        price = float(price.replace(",", ""))

        if price < 60000:
            email_from, password, email_to = get_info()
            subject = "Price fell down!"
            body = f"The price for the product you are tracking has fallen down to {price}. Check the link: {url}"

            send_email(email_from, password, email_to, subject, body)

    except ValueError:
        print("Price is not available.")
        return


def job():
    url = "https://amzn.asia/d/iyf84US"
    track_price(url)


if __name__ == "__main__":

    schedule.every(2).hours.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)
