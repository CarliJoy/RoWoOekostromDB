from email.message import Message

import gnupg
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, SafeMIMEMultipart, SafeMIMEText
from django.utils.log import AdminEmailHandler


class EmailMultiAlternativesEncrypted(EmailMultiAlternatives):
    def __init__(self, *args, recipient_key_id: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.gpg = gnupg.GPG()
        self.recipient_key_id = recipient_key_id

    def _create_message(self, msg: SafeMIMEText):
        # Step 1: Create the inner message
        inner_msg = super()._create_message(
            msg
        )  # Generates the fully structured inner message

        # Encrypt the inner message content
        encrypted_data = self.gpg.encrypt(
            inner_msg.as_string(), self.recipient_key_id, always_trust=True
        )
        if not encrypted_data.ok:
            raise Exception("Failed to encrypt email content")

        # Step 2: Create the outer PGP/MIME structure
        outer_msg = SafeMIMEMultipart("encrypted")

        # PGP control part
        control_part = Message()
        control_part.add_header("Content-Type", "application/pgp-encrypted")
        control_part.add_header("Content-Transfer-Encoding", "7bit")
        control_part.attach("Version: 1")
        outer_msg.attach(control_part)

        # Encrypted data part
        encrypted_part = Message()
        encrypted_part.add_header("Content-Type", "application/octet-stream")
        encrypted_part.add_header("Content-Disposition", 'inline; filename="msg.asc"')
        encrypted_part.add_header("Content-Transfer-Encoding", "7bit")
        encrypted_part.attach(str(encrypted_data))
        outer_msg.attach(encrypted_part)

        return outer_msg


class GPGAdminEmailHandler(AdminEmailHandler):
    def __init__(self, recipient_key_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gpg = gnupg.GPG()
        self.recipient_key_id = recipient_key_id
        # Use settings for from_email and recipient_list
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.recipient_list = [email for name, email in settings.ADMINS]

    def send_mail(self, subject, message, html_message=None, *args, **kwargs):  # noqa: ARG002
        if not settings.ADMINS:
            return
        len_wanted = 2
        if not all(
            isinstance(a, list | tuple) and len(a) == len_wanted
            for a in settings.ADMINS
        ):
            raise ValueError("The ADMINS setting must be a list of 2-tuples.")
        mail = EmailMultiAlternativesEncrypted(
            f"{settings.EMAIL_SUBJECT_PREFIX}{subject}",
            message,
            settings.SERVER_EMAIL,
            [a[1] for a in settings.ADMINS],
            connection=self.connection(),
            recipient_key_id=self.recipient_key_id,
        )
        if html_message:
            mail.attach_alternative(html_message, "text/html")
        mail.send(fail_silently=True)
