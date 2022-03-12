

class Config:
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'citoyen.x14@gmail.com'
    MAIL_PASSWORD = 'cncbtzywxvuifwva'

    MAIL_DEBUG = True
    MAIL_SUPPRESS_SEND = False

    MAIL_DEFAULT_SENDER = ('SIB@admin.com', 'Alarm App Flask')
    MAIL_MAX_EMAILS = None
    MAIL_ASCII_ATTACHMENTS = False
