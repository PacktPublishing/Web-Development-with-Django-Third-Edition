from itertools import groupby
from django.core.mail import send_mass_mail
from django.tasks import task
from django.template.loader import render_to_string

from .models import Review
from .utils import get_daterange_dt


@task(priority=2, queue_name="default")
def review_report(emails, from_email, period, start_day, site="http://127.0.0.1:8000"):

    start_day_dt, end_day_dt = get_daterange_dt(start_day, period)
    
    start_day_fmt = start_day_dt.strftime('%x')
    end_day_fmt = end_day_dt.strftime('%x')

    reviews = Review.objects.filter(date_created__range=[start_day_dt, end_day_dt]).order_by('book__title')
    
    context = dict(period=period, start_day_fmt=start_day_fmt, end_day_fmt=end_day_fmt, site=site,
                   reviews_by_title=[(title, list(reviews)) for title, reviews in groupby(reviews, lambda x: x.book.title)])

    if period=='daily':
        subject = f"Your {period} Bookr reviews for {start_day_fmt}"
    else:
        subject = f"Your {period} Bookr reviews from {start_day_fmt} to {end_day_fmt}"
    message = render_to_string('reviews/review_report_email.txt', context)

    email_messages = [(subject, message, from_email, [email]) for email in emails]
    return send_mass_mail(email_messages, fail_silently=False)
    # return send_mail(subject, message, from_email, recipient_list=emails)
