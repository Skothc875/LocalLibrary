from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin 
from datetime import timedelta
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from .forms import RenewBookForm
from django.db.models import ProtectedError, RestrictedError
from django.urls import reverse_lazy
from django.views import generic
from .models import Author

# Create your views here.
from .models import Book, Author, BookInstance, Genre

def index(request):
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()

    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count()

    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1

    return render(
        request,
        'index.html',
        context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors,'num_visits':num_visits},
)
from django.views import generic

class BookListView(generic.ListView):
    model = Book
    paginate_by = 2

class BookDetailView(generic.DetailView):
    model = Book

from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Generic class-based view listing books on loan to current user.
    """
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self):
        return BookInstance.objects.filter(status='o').order_by('due_back')

@login_required
@permission_required("catalog.can_mark_returned", raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk, status="o")

    if request.method == "POST":
        form = RenewBookForm(request.POST)
        if form.is_valid():
            book_instance.due_back = form.cleaned_data["renewal_date"]
            book_instance.save(update_fields=["due_back"])
            return redirect("all-borrowed")
    else:
        form = RenewBookForm(
            initial={"renewal_date": timezone.localdate() + timedelta(weeks=3)}
        )

    return render(request, "catalog/book_renew_librarian.html", {
        "form": form,
        "book_instance": book_instance,
    })

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10
    ordering = ["last_name", "first_name", "pk"]

class AuthorDetailView(generic.DetailView):
    model = Author


class AuthorCreate(PermissionRequiredMixin, generic.CreateView):
    model = Author
    fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]
    permission_required = "catalog.add_author"
    success_url = reverse_lazy("authors")


class AuthorUpdate(PermissionRequiredMixin, generic.UpdateView):
    model = Author
    fields = AuthorCreate.fields
    permission_required = "catalog.change_author"
    success_url = reverse_lazy("authors")


class AuthorDelete(PermissionRequiredMixin, generic.DeleteView):
    model = Author
    permission_required = "catalog.delete_author"
    success_url = reverse_lazy("authors")

    def form_valid(self, form):
        if self.object.book_set.exists():
            return self.render_to_response(self.get_context_data(
                form=form,
                error="У этого автора есть книги. Сначала убери связь с автором у этих книг.",
            ))
        try:
            return super().form_valid(form)
        except (ProtectedError, RestrictedError):
            return self.render_to_response(self.get_context_data(
                form=form,
                error="Запись автора используется в каталоге.",
            ))