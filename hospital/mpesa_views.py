import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from .models import Bill
from .mpesa import trigger_stk_push


@login_required
def initiate_mpesa_payment(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)

    if bill.is_paid:
        messages.info(request, f'Invoice #AHC-{bill.id:04d} is already paid.')
        return redirect('print_invoice', bill_id=bill.id)

    if request.method == 'POST':
        phone = request.POST.get('phone_number', '').strip()
        if not phone:
            messages.error(request, 'Please enter a valid M-Pesa phone number.')
            return redirect('initiate_mpesa_payment', bill_id=bill.id)

        try:
            res_data, formatted_phone = trigger_stk_push(
                phone_number=phone,
                amount=bill.total_amount,
                account_reference=f"AHC-{bill.id:04d}",
                transaction_desc="Ayunda Health Center Bill",
            )

            if res_data.get('ResponseCode') == '0':
                bill.mpesa_checkout_id = res_data.get('CheckoutRequestID')
                bill.mpesa_phone = formatted_phone
                bill.save()
                messages.success(
                    request,
                    f"M-Pesa STK Push sent to {formatted_phone}. Enter your M-Pesa PIN on your phone, then refresh this invoice."
                )
                return redirect('print_invoice', bill_id=bill.id)
            else:
                error_msg = res_data.get('errorMessage') or res_data.get('ResponseDescription', 'STK Push failed.')
                messages.error(request, f"M-Pesa Error: {error_msg}")
        except Exception as e:
            messages.error(request, f"Could not connect to Safaricom Daraja API: {e}")

    default_phone = bill.appointment.patient.user.phone_number or ''
    return render(request, 'hospital/mpesa_pay.html', {
        'bill': bill,
        'default_phone': default_phone,
    })


@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))
            stk_callback = body.get('Body', {}).get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            checkout_id = stk_callback.get('CheckoutRequestID')

            if result_code == 0 and checkout_id:
                bill = Bill.objects.filter(mpesa_checkout_id=checkout_id).first()
                if bill:
                    items = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                    receipt = next(
                        (i.get('Value') for i in items if i.get('Name') == 'MpesaReceiptNumber'),
                        None,
                    )
                    bill.is_paid = True
                    if receipt:
                        bill.mpesa_receipt_number = receipt
                    bill.save()
        except Exception:
            pass

    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
