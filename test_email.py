import os
import django
from django.core.mail import send_mail
from pathlib import Path
from dotenv import load_dotenv

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
dotenv_path = BASE_DIR / '.env'
load_dotenv(dotenv_path)

# Send test email
try:
    send_mail(
        subject='Test',
        message='Test email from Django',
        from_email='lernagorc90@gmail.com',
        recipient_list=['aleksanjhangiryan@gmail.com'],
        fail_silently=False
    )
    print('Email sent successfully!')
except Exception as e:
    print(f'Failed to send email: {str(e)}')