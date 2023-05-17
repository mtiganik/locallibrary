from typing import Any
import datetime
from .models import Book, Author, BookInstance, Genre
from django.db.models.query import QuerySet
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin 
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from catalog.forms import RenewBookForm

from django.core.exceptions import PermissionDenied

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

def renew_book_librarian(request, pk):

    if not request.user.is_staff:
        raise PermissionDenied()

    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


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
    paginate_by = 10



class AuthorListView(generic.ListView):
    model = Author

# @login_required
class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author

class BookDetailView(generic.DetailView):
    model = Book

class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    # initial = {'date_of_death': '11/06/2020'}

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
    model = Author
    fields = '__all__' #not recommended (potential security issue if more fields added)
    success_url = reverse_lazy('authors')

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
    model = Author
    success_url = reverse_lazy('authors')

class BookCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    model = Book
    success_url = reverse_lazy('books')

class BookUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
    fields = '__all__'
    model = Book
    success_url = reverse_lazy('books')


class BookDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
    model = Book
    success_url = reverse_lazy('books')
