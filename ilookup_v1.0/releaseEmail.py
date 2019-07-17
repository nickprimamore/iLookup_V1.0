import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

utility = email.utils

class Email:
    def sendEmail(self, releaseChanges):
        # Replace sender@example.com with your "From" address.
        # This address must be verified.
        print(releaseChanges)
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
        SUBJECT = 'Amazon SES Test (Python smtplib)'

        # The HTML body of the email.
        BODY_HTML = """<html>
        <head></head>
        <body>
          <h1>The Following Cluster Need Releases Updated</h1>
          <p>This email was sent with Amazon SES using the
            <a href='https://www.python.org/'>Python</a>
            <a href='https://docs.python.org/3/library/smtplib.html'>
            smtplib</a> library.</p>
        </body>
        </html>
                    """

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

# email = Email()
#
# email.sendEmail("hello")
