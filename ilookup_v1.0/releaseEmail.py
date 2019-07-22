import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

utility = email.utils
class Email:
    def saveUnknowns(self, prodObject):
        print("THIS IS THE EMAIL FUNCTION", prodObject)
        unknowns.append(prodObject)

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
        <body>"""

        if len(clusters) > 0:
            for object in clusters:
                clusterName = object["Cluster"]
                productName = object["Product"]
                releaseList = object["Releases"]
                htmlStr += "<h3>" + clusterName + ": " + productName + "</h3><ul>"
                for release in releaseList:
                    htmlStr += "<li>" + release + "</li>"
                htmlStr += "</ul>"

        htmlStr += """<p>This email was sent with Amazon SES using the
            <a href='https://www.python.org/'>Python</a>
            <a href='https://docs.python.org/3/library/smtplib.html'>
            smtplib</a> library.</p></body></html>"""

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

email.sendEmail([{"Cluster": "asg-ecs-qa2-cluster", "Product": "iConductor", "Releases": ["2019-07-15 18:27:09.762688", "2019-07-15 18:27:33.138756"]},
        {"Cluster": "asg-uat-iconductor-cluster", "Product": "iConductor", "Releases": ["2019-07-16 19:18:56.178954", "2019-07-16 19:19:09.410748"]}])
