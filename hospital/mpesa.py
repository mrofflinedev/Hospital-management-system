import base64
from datetime import datetime
import requests
from django.conf import settings


def format_kenyan_phone(phone):
    phone = str(phone).strip().replace('+', '').replace(' ', '')
    if phone.startswith('0'):
        return '254' + phone[1:]
    if phone.startswith('7') or phone.startswith('1'):
        return '254' + phone
    return phone


def get_base_url():
    env = str(getattr(settings, 'MPESA_ENVIRONMENT', 'sandbox')).strip().lower()
    if env == 'sandbox':
        return 'https://safaricom.co.ke'
    return 'https://safaricom.co.ke'


def get_mpesa_access_token():
    url = f"{get_base_url()}/oauth/v1/generate?grant_type=client_credentials"
    headers = {
        'User-Agent': 'AyundaHealthCenter/1.0',
    }
    response = requests.get(
        url,
        auth=(settings.MPESA_CONSUMER_KEY.strip(), settings.MPESA_CONSUMER_SECRET.strip()),
        headers=headers,
        timeout=15,
    )
    response.raise_for_status()
    return response.json().get('access_token')


def trigger_stk_push(phone_number, amount, account_reference, transaction_desc):
    access_token = get_mpesa_access_token()
    stk_url = f"{get_base_url()}/mpesa/stkpush/v1/processrequest"

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    raw_password = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    password = base64.b64encode(raw_password.encode()).decode('utf-8')
    formatted_phone = format_kenyan_phone(phone_number)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'User-Agent': 'AyundaHealthCenter/1.0',
    }

    payload = {
        'BusinessShortCode': settings.MPESA_SHORTCODE,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': int(round(float(amount))),
        'PartyA': formatted_phone,
        'PartyB': settings.MPESA_SHORTCODE,
        'PhoneNumber': formatted_phone,
        'CallBackURL': settings.MPESA_CALLBACK_URL,
        'AccountReference': account_reference,
        'TransactionDesc': transaction_desc,
    }

    response = requests.post(stk_url, json=payload, headers=headers, timeout=20)
    return response.json(), formatted_phone
