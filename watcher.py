from requests_html import HTMLSession
import time
import smtplib


sender_email = '@gmail.com'
password = ''
smtp_server = "smtp.gmail.com"
port = 587
receivers = ['yousif.mazeh@gmail.com']


def get_links(url):
    return session.get(url).html.absolute_links


def get_content(url, field):
    return session.get(url).html.find(field)
     


def check_us_treasury():
    global init_sanctions
    lookup_keywords = ['lebanon', 'lebanese', 'beirut', 'syria', 'korea']
    f = get_links("https://home.treasury.gov/policy-issues/financial-sanctions/recent-actions")
    lookup_link = "recent-actions/202"
    new_update = [d for d in f if lookup_link in d]
    new_update.sort()
    if init_sanctions != new_update[-1]:
        init_sanctions = new_update[-1]
        print('New Sanction added!', init_sanctions)
        content = get_content(init_sanctions, '.content')
        for word in lookup_keywords:
            if word in content[0].text.lower():
                send_emails(True)
                break
                


def init_email():
    global server 
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.ehlo()
    server.login(sender_email, password)

def send_emails(treasuryUpdated=False, bdlUpdated=False):
    if treasuryUpdated:
        subject = 'US treasury has add new sanctions'
        message = '\nThe US treasury has added new sactions that might concern Lebanon, you can check it on the following link:\n'
        name = "US Treasury Update"
        link = init_sanctions
    elif bdlUpdated:
        subject = 'BDL balance sheet update'
        message = '\nBDL updated its balance sheet, you can download it from the following link:\n'
        name = "BDL Update"
        link = init_file
    for receiver in receivers:
        server.sendmail(sender_email, receiver, build_message(receiver, name, subject, message, link))


session = HTMLSession()

init_file = ''
init_sanctions = ''

def check_for_updates():
    global init_file
    print('Checking...')
    f = get_links("https://bdl.gov.lb/tabs/index/6/287/BDL-Balance-Sheet.html")
    lookup_link = 'files/tabs/'
    new_file = [d for d in f if lookup_link in d]
    if new_file[0] != init_file:
        init_file = new_file[0]
        print("BDL data updated", init_file)
        send_emails(bdlUpdated=True)
        
        

def build_message(receiver, name, subject, message, link):
    msg_header = 'From: {} <{}>\n' \
             'To: <{}>\n' \
             'Subject: {}\n'.format(name, sender_email, receiver, subject)
    msg_content =  '{} {}'.format(message, link)
    msg = ''.join([msg_header, msg_content])
    return msg
        


init_email()

while True:
    try:
        check_for_updates()
        check_us_treasury()
        print('Checking again in 60 seconds.')
    except Exception as e:
        print('Error! ', e)
    
    time.sleep(60)

