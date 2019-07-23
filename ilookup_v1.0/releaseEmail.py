import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app import app, db
from sqlalchemy import func
from app.models import Client, Product, Product_Release, Cluster, Component, Task_Definition, CPRC


utility = email.utils
class Email:
    def getRecords(self):

        print("in record function")
        records = db.session.query(Product.product_name, Cluster.cluster_name, Cluster.environment, Product_Release.release_number, Product_Release.inserted_at).filter(CPRC.cluster_id==Cluster.cluster_id, CPRC.product_release_id==Product_Release.product_release_id, Product.product_id==Product_Release.product_id
        ).filter(func.length(Product_Release.release_number)>11).filter(Cluster.environment!="DEV").all()

        emails = Email()
        emails.sendEmail(records)

    def sendEmail(self, clusters):
        # Replace sender@example.com with your "From" address.
        # This address must be verified.
        #print(releaseChanges)
        SENDER = 'kpatel@acord.org'
        SENDERNAME = 'Krish Patel'

        # Replace recipient@example.com with a "To" address. If your account
        # is still in the sandbox, this address must be verified.
        RECIPIENT  = 'nprimamore@acord.org'

        # Replace smtp_username with your Amazon SES SMTP user name.
        USERNAME_SMTP = "AKIAIQKUKM5GTVBDWHFA"

        # Replace smtp_password with your Amazon SES SMTP password.
        PASSWORD_SMTP = "BBnN14ceLJSjHEbqgks91ckWP5lxjLRluLKNdoPSzk20"

        # (Optional) the name of a configuration set to use for this message.


        # If you're using Amazon SES in an AWS Region other than US West (Oregon),
        # replace email-smtp.us-west-2.amazonaws.com with the Amazon SES SMTP
        # endpoint in the appropriate region.
        HOST = "email-smtp.us-east-1.amazonaws.com"
        PORT = 587

        # The subject line of the email.
        SUBJECT = 'Release Numbers Needed - iLookup'

        #Dummy cluster/release/product info for testing

        htmlStr = """<html>
        <head>
            <h3>The following clusters need their timestamps updated to release numbers:</h3>
        </head>
        <body>
        """

        dates = []
        strData = []
        prodRecords = {}
        if len(clusters) > 0:
            for x in clusters:
                strDate = ""
                if x[4][0: 10] not in dates:
                    if x[4][5: 7] == "01":
                        strDate = strDate + "January"
                    elif x[4][5: 7] == "02":
                        strDate = strDate + "February"
                    elif x[4][5: 7] == "03":
                        strDate = strDate + "March"
                    elif x[4][5: 7] == "04":
                        strDate = strDate + "April"
                    elif x[4][5: 7] == "05":
                        strDate = strDate + "May"
                    elif x[4][5: 7] == "06":
                        strDate = strDate + "June"
                    elif x[4][5: 7] == "07":
                        strDate = strDate + "July"
                    elif x[4][5: 7] == "08":
                        strDate = strDate + "August"
                    elif x[4][5: 7] == "09":
                        strDate = strDate + "September"
                    elif x[4][5: 7] == "10":
                        strDate = strDate + "October"
                    elif x[4][5: 7] == "11":
                        strDate = strDate + "November"
                    else:
                        strDate = strDate + "December"
                    strDate = strDate + " " + x[4][8: 10] + ", " + x[4][0: 4]
                    strData.append(strDate)
                    dates.append(x[4][0: 10])
                    prodRecords[x[4][0:10]] = []
            for x in clusters:
                prodRecords[x[4][0:10]].append([x[0], x[1], x[2], x[3], x[4]])

        for x in dates:
            htmlStr += """<h3>""" + strData[0] + """</h3>""" + """<ul>"""
            for x in prodRecords[x[0: 10]]:
                htmlStr += """<li>""" + x[0] + """, """ + x[1] + """, """ + x[2] + """, """ + x[3] + """</li>"""
            htmlStr += """</ul>"""


        htmlStr += """<p>Have a nice day!</p></body></html>"""

        # The HTML body of the email.
        BODY_HTML = htmlStr

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = utility.formataddr((SENDERNAME, SENDER))
        msg['To'] = RECIPIENT

        # Record the MIME types of both parts - text/plain and text/html.
        part2 = MIMEText(BODY_HTML, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part2)

        # Try to send the message.
        try:
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls()
            #stmplib docs recommend calling ehlo() before & after starttls()
            server.ehlo()
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            server.close()
        # Display an error message if something goes wrong.
        except Exception as e:
            print ("Error: ", e)
        else:
            print ("Email sent!")

email = Email()
email.getRecords()
