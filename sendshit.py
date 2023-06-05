import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import itertools
import concurrent.futures
from email.headerregistry import Address
from email.utils import formataddr

logo = """
█████████████████████████████████████████████████████
█─▄─▄─█─█─█▄▄▄░█▄─▄─▀██▀▄─██▄─▀█▄─▄█▄─█─▄█▄▄▄░█▄─▄▄▀█
███─███─▄─██▄▄░██─▄─▀██─▀─███─█▄▀─███─▄▀███▄▄░██─▄─▄█
▀▀▄▄▄▀▀▄▀▄▀▄▄▄▄▀▄▄▄▄▀▀▄▄▀▄▄▀▄▄▄▀▀▄▄▀▄▄▀▄▄▀▄▄▄▄▀▄▄▀▄▄▀
"""

print(logo)

def read_lines_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
    return lines


def read_html_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content


def send_email(smtp_info, sender_name, to_addr, subject, body, timeout=10):
    from_addr = smtp_info[2]
    port = smtp_info[1]

    msg = MIMEMultipart()
    msg['From'] = formataddr((sender_name, from_addr))
    msg['To'] = to_addr
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(smtp_info[0], port, timeout=timeout)
        server.ehlo()
        if server.has_extn('STARTTLS'):
            server.starttls()
            server.ehlo()
        server.login(from_addr, smtp_info[3])
        server.sendmail(from_addr, to_addr, msg.as_string())
        server.quit()
        print(f"Email sent to {to_addr} using {from_addr} with sender name {sender_name}")
        return True
    except Exception as e:
        print(f"Error sending email to {to_addr} using {from_addr} with sender name {sender_name}: {e}")
        return False


def send_email_with_next_smtp(smtps_cycle, sender_name, to_addr, subject, html_body, timeout=10):
    success = False
    while not success:
        smtp_info = next(smtps_cycle)

        # Replace [-email-] in the HTML body with the actual recipient's email address
        body = html_body.replace('[-email-]', to_addr)

        success = send_email(smtp_info, sender_name, to_addr, subject, body, timeout)
    return success


def main():
    smtp_file = input("Enter the SMTP file path: ")
    smtps = [line.split('|') for line in read_lines_from_file(smtp_file)]
    smtps_cycle = itertools.cycle(smtps)

    sender_name = input("Enter the sender name: ")

    email_list_file = input("Enter the email list file path: ")
    email_list = read_lines_from_file(email_list_file)

    subject = input("Enter the email subject: ")
    html_body_file = input("Enter the HTML body file path: ")
    html_body = read_html_content(html_body_file)

    # Prompt user for number of threads
    num_threads = int(input("Enter number of threads: "))

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(send_email_with_next_smtp, smtps_cycle, sender_name, email, subject, html_body) for email in email_list]
        concurrent.futures.wait(futures)


if __name__ == "__main__":
    main()

