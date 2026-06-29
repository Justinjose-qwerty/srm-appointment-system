# SRM Student Appointment Scheduling System

## Public Deployment

This project is designed to be public-deployable. Do not keep personal credentials in the codebase.

Set these environment variables in production:

- `DJANGO_SECRET_KEY` - a unique secret key
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS=yourdomain.com,127.0.0.1,localhost`
- `ADMIN_USERNAME` - admin username for the SRM dashboard
- `ADMIN_PASSWORD` - admin password for the SRM dashboard
- `DEFAULT_FROM_EMAIL` - sender email address
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USE_TLS`
- `EMAIL_USE_SSL`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`

## OTP Email Setup

The OTP flow uses Django's email backend. For Gmail delivery, set these environment variables:

- `EMAIL_HOST=smtp.gmail.com`
- `EMAIL_PORT=587`
- `EMAIL_USE_TLS=True`
- `EMAIL_USE_SSL=False`
- `EMAIL_HOST_USER=yourgmail@gmail.com`
- `EMAIL_HOST_PASSWORD=your-gmail-app-password`
- `DEFAULT_FROM_EMAIL=yourgmail@gmail.com`

Use a Gmail App Password, not your normal account password.

If SMTP credentials are not set, the app falls back to the console backend for local development.
