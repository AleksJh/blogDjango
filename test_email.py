#!/usr/bin/env python
"""
Test Email Script for Django Blog Application

This script tests the email functionality of the Django blog application
by sending a test email using the configured email settings in .env file.

Usage:
    python test_email.py
"""

import os
from pathlib import Path

import django
from django.core.mail import send_mail
from dotenv import load_dotenv

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path)  # This makes environment variables available via os.getenv()

# Attempt to send a test email using Django's send_mail function
try:
    # Send email with test content
    send_mail(
        subject="Test",  # Email subject
        message="Test email from Django",  # Email body
        from_email="lernagorc90@gmail.com",  # Sender email (should match
        # EMAIL_HOST_USER in .env)
        recipient_list=["aleksanjhangiryan@gmail.com"],  # List of recipients
        fail_silently=False,  # Raise exceptions on errors
    )
    print("Email sent successfully!")
except Exception as e:
    # Print detailed error message if email sending fails
    print(f"Failed to send email: {str(e)}")
