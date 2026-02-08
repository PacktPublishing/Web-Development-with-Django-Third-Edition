import csv
from datetime import datetime
from io import BytesIO

from PIL import Image
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import (login_required, user_passes_test)
from django.contrib.staticfiles.finders import find
from django.core.exceptions import PermissionDenied
from django.core.files.images import ImageFile
from django.db.models import Avg, Count
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import get_template
from plotly.offline import plot
import plotly.graph_objects as go
from weasyprint import HTML, CSS

from .forms import PublisherForm, SearchForm, ReviewForm, BookMediaForm
from .models import Book, Contributor, Publisher, Review
from .utils import average_rating, ratings_to_histogram, format_workbook 


def index(request):
    return render(request, "base.html")


def book_search(request):
    search_text = request.GET.get("search", "")
    search_history = request.session.get("search_history", [])
    form = SearchForm(request.GET)
    books = set()

    if form.is_valid() and form.cleaned_data["search"]:
        search = form.cleaned_data["search"]
        search_in = form.cleaned_data.get("search_in") or "title"
        if search_in == "title":
            books = Book.objects.filter(title__icontains=search)
        else:
            fname_contributors = Contributor.objects.filter(
                first_names__icontains=search
            )

            for contributor in fname_contributors:
                for book in contributor.book_set.all():
                    books.add(book)

            lname_contributors = Contributor.objects.filter(
                last_names__icontains=search
            )

            for contributor in lname_contributors:
                for book in contributor.book_set.all():
                    books.add(book)
        if request.user.is_authenticated:
            search_history.append([search_in, search])
            request.session["search_history"] = search_history
    elif search_history:
        initial = dict(search=search_text, search_in=search_history[-1][0])
        form = SearchForm(initial=initial)

    return render(
        request,
        "reviews/search-results.html",
        {"form": form, "search_text": search_text, "books": books},
    )


def welcome_view(request):
    return render(request, 'base.html')


def book_list(request):
    books = Book.objects.all()
    book_list = []
    for book in books:
        reviews = book.review_set.all()
        if reviews:
            book_rating = average_rating([review.rating for review in reviews])
            number_of_reviews = len(reviews)
        else:
            book_rating = None
            number_of_reviews = 0
        book_list.append({
            'book': book,
            'book_rating': book_rating,
            'number_of_reviews': number_of_reviews})
    context = {
        'book_list': book_list
    }
    return render(request, "reviews/book_list.html", context)


def _book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    reviews = book.review_set.all()
    if reviews:
        ratings = [review.rating for review in reviews]
        book_rating = average_rating(ratings)
        book_rating_histogram = ratings_to_histogram(ratings)
        context = {
            "book": book,
            "book_rating": book_rating,
            "book_rating_histogram": book_rating_histogram,
            "reviews": reviews
        }
    else:
        context = {
            "book": book,
            "book_rating": None,
            "book_rating_histogram": None,
            "reviews": None
        }
    if request.user.is_authenticated:
        max_viewed_books_length = 10
        viewed_books = request.session.get('viewed_books', [])
        viewed_book = [book.id, book.title]
        if viewed_book in viewed_books:
            viewed_books.pop(viewed_books.index(viewed_book))
        viewed_books.insert(0, viewed_book)
        viewed_books = viewed_books[:max_viewed_books_length]
        request.session['viewed_books'] = viewed_books
        request.session['viewed_books'] = viewed_books
    return request, context


def book_detail(request, pk):
    request, context = _book_detail(request, pk)
    return render(request, "reviews/book_detail.html", context)


def book_detail_pdf(request, pk):
    request, context = _book_detail(request, pk)
    # Render the HTML
    template = get_template('reviews/book_detail_pdf.html')
    html = template.render(context=context, request=request)

    # find the system path of the weasyprint css file.
    css = CSS(find('weasyprint.css'))

    # Write the PDF binary
    pdf_stream = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(stylesheets=[css])

    # Create a response
    fname = f"book_detail_{context['book'].isbn or context['book'].id}.pdf"
    cdisposition = f"inline; filename={fname}"
    response = HttpResponse(pdf_stream, content_type='application/pdf')
    response['Content-Disposition'] = cdisposition
    response['Content-Transfer-Encoding'] = 'binary'

    return response


def is_staff_user(user):
    return user.is_staff


@user_passes_test(is_staff_user)
def publisher_edit(request, pk=None):
    if pk is not None:
        publisher = get_object_or_404(Publisher, pk=pk)
    else:
        publisher = None

    if request.method == "POST":
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            updated_publisher = form.save()
            if publisher is None:
                messages.success(request,
                                 f'Publisher "{updated_publisher}" was created.')
            else:
                messages.success(request,
                                 f'Publisher "{updated_publisher}" was updated.')

            return redirect("publisher_edit", updated_publisher.pk)
    else:
        form = PublisherForm(instance=publisher)

    return render(
        request,
        "reviews/instance-form.html",
        {
            "method": request.method,
            "form": form,
            "model_type": "Publisher",
            "instance": publisher,
        },
    )


@login_required
def review_edit(request, book_pk, review_pk=None):
    book = get_object_or_404(Book, pk=book_pk)

    if review_pk is not None:
        review = get_object_or_404(Review, book_id=book_pk, pk=review_pk)
        user = request.user
        if not user.is_staff and review.creator.id != user.id:
            raise PermissionDenied
    else:
        review = None

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            updated_review = form.save(False)
            updated_review.book = book

            if review is None:
                messages.success(request, f'Review for "{book}" created.')
            else:
                updated_review.date_edited = timezone.now()
                messages.success(request, f'Review for "{book}" updated.')

            updated_review.save()
            return redirect("book_detail", book.pk)
    else:
        form = ReviewForm(instance=review)

    return render(
        request,
        "reviews/instance-form.html",
        {
            "form": form,
            "instance": review,
            "model_type": "Review",
            "related_instance": book,
            "related_model_type": "Book",
        },
    )


@login_required
def book_media(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        form = BookMediaForm(request.POST,
        request.FILES, instance=book)

        if form.is_valid():
            book = form.save(False)
            cover = form.cleaned_data.get("cover")
            if cover:
                image = Image.open(cover)
                image.thumbnail((300, 300))
                image_data = BytesIO()
                image.save(fp=image_data, format=cover.image.format)
                image_file = ImageFile(image_data)
                book.cover.save(cover.name, image_file)
            book.save()
            messages.success(request, f"Book {book} was successfully updated.")
            return redirect("book_detail", book.pk)
    else:
        form = BookMediaForm(instance=book)

    return render(request, "reviews/instance-form.html",
                  {"instance": book, "form": form, "model_type": "Book", "is_file_upload":True})

def _review_summary():
    # Retrieve the data
    books = Book.objects.all()
    header = ['title', 'isbn', 'publisher', 'reviewer', 'rating']
    rows = [header]
    for book in books:
        reviews = book.review_set.all()
        if reviews:
            rows.append([book.title, book.isbn, book.publisher.name,
                         reviews[0].creator.username, reviews[0].rating])
        for review in reviews[1:]:
                rows.append(['', '', '',
                    review.creator.username,
                    review.rating])
    return rows


def review_summary_csv(request):
    rows = _review_summary()
    response = HttpResponse(content_type='text/csv')
    filename = "review_summary.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    # Write the CSV response
    writer = csv.writer(response)
    for row in rows:
        writer.writerow(row)
    return response


def review_summary_xlsx(request):
    rows = _review_summary()

    format_settings = dict(
         header = dict(bold=True, font_size=12,
                       bg_color= 'gray'),
         short_text= dict(align='left'),
         isbn = dict(num_format= '0', align= 'left'),
         content = dict(align= 'left', valign='top',
                        text_wrap= True),
         rating = dict(num_format= '#', align= 'right'),
         footer = dict(bold= True, font_size=12),
         average = dict(num_format= '#.###', align='right',
                        bold= True, font_size=12),
    )

    # Column A 40, B 15, C-D 30, E 50, F 5
    column_widths = [('A:A', 40), ('B:B', 14), ('C:D', 30),
                ('E:E', 50), ('F:F', 5),]

    # title, isbn, publisher, reviewer, content, rating
    col_formats = ('short_text', 'isbn', 'short_text',
                   'short_text', 'content', 'rating')

    # Create BytesIO object and instantiate Workbook
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)

    workbook = format_workbook(workbook, rows, format_settings,
                               reader.fieldnames, col_formats, column_widths, 
                               footer_avg=dict(
                                   label='Average Rating', id='rating'))

    # Close the workbook
    workbook.close()
    # Rewind the buffer.
    output.seek(0)
    # Create the HTTP response.
    filename = 'review_details.xlsx'
    ctype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(output, content_type=ctype)
    response['Content-Disposition'] = f'attachment; filename={filename}' 
    return response


def review_statistics(request, min_publication_year, max_publication_year):
    min_year = datetime(min_publication_year, 1, 1)
    max_year = datetime(max_publication_year, 12, 31, 23, 59, 59)

    reviews = Review.objects.filter(
        book__publication_date__gte=min_year,
        book__publication_date__lte=max_year).values(
              'book__id', 'book__title', 'book__publication_date'
        ).annotate(average_rating=Avg('rating')
        ).annotate(num_rating=Count('rating'))

    scatter_0 = go.Scatter(
        x=[review['book__publication_date'].year for review in reviews],
        y=[review['average_rating'] for review in reviews],
        text=[review['book__title'] for review in reviews],
        mode='markers+text',
        textposition='middle center',
        marker=dict(
            size=[review['num_rating'] for review in reviews],
            sizemode='area',
            sizeref=0.001,
        )
    )

    layout = go.Layout(autosize=True, height=900)
    fig = go.Figure(data=[scatter_0], layout=layout)
    fig.update_xaxes(range=[min_publication_year, max_publication_year])
    fig.update_yaxes(range=[-0.2, 5.2])

    plotly_div = plot(fig, output_type='div')
    return render(request, "reviews/statistics.html", context={'plotly_div': plotly_div})


def get_review_profile_img(image_type, user_id, background_path):
    covers = [str(review.book.cover) for review in Review.objects.filter(creator_id=user_id)]
    bg = Image.open(settings.MEDIA_ROOT / background_path)
    bg_img = bg.convert('RGBA')
    orientations = [135, -135, 120, 0, -120, 105, -105]
    orientations = [30, -15, 15, 0, -30, 45, -45]
    heights = [125, 150, 175, 150, 125, 100, 150]
    for i, cover in enumerate(covers):
        orientation = orientations[i%len(orientations)]
        x_pos = int(-10 + i*1000/len(covers))
        y_pos = heights[i%len(heights)]
        cover_img = Image.open(settings.MEDIA_ROOT / cover).convert('RGBA')
        
        rot = cover_img.rotate(orientation, Image.NEAREST, expand=1)
        bg_img.paste(rot, box=(x_pos, y_pos), mask=rot)

    if image_type == 'jpg':
        bg_img = bg_img.convert('RGB')

    return bg_img


def reviewer_profile_png(request, user_id):
    image = get_review_profile_img('png', user_id, 'backgrounds/wood_background.jpg')
    image_io = BytesIO()
    image.save(image_io, format='PNG')
    return HttpResponse(image_io.getvalue(), content_type="image/png")


def reviewer_profile_jpg(request, user_id):
    image = get_review_profile_img('jpg', user_id, 'backgrounds/wood_background.jpg')
    image_io = BytesIO()
    image.save(image_io, format='JPEG')
    return HttpResponse(image_io.getvalue(), content_type="image/jpeg")


def logo_transormations(request):
    logo = 'reviews/static/reviews/logo.png'
    background = 'media/backgrounds/wood_background.jpg'
    transformed_img = _logo_transormations(logo, background)

    response = HttpResponse(content_type="image/png;")
    transformed_img.save(response, 'PNG', quality=95)
    return response

