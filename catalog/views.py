from typing import Any
from django.db.models.query import QuerySet
from .models import Book, Author, BookInstance, Genre
from django.shortcuts import render
from django.views import generic
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    num_authors = Author.objects.count()
    num_visits = request.session.get('num_visits',0)
    request.session['num_visits'] = num_visits + 1
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits':num_visits
    }

    return render(request, 'index.html', context=context)

class AllBorrowedListView(LoginRequiredMixin, generic.ListView):
    template_name = 'catalog/all_borrowed_list.html'
    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')

    model = BookInstance
    def get_queryset(self):
        return(
            BookInstance.objects.filter(status__exact='o').order_by('due_back')
        )
    # model = BookInstance.objects.filter(status__exact='o').order_by('due_back')


class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )


# Generic class way
class BookListView(generic.ListView):
    model = Book
    paginate_by = 3



class AuthorListView(generic.ListView):
    model = Author

# @login_required
class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author

class BookDetailView(generic.DetailView):
    model = Book
