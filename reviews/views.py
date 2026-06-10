from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import DeleteView, UpdateView

from store.models import Product

from .forms import ReviewForm
from .models import Review


@login_required
def review_create(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.warning(request, "You have already reviewed this product.")
        return redirect("product_detail", slug=product_slug)
    form = ReviewForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()
        messages.success(request, "Your review has been posted.")
        return redirect("product_detail", slug=product_slug)
    return render(request, "reviews/review_form.html", {"form": form, "product": product})


class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = "reviews/review_form.html"

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse("product_detail", kwargs={"slug": self.object.product.slug})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["product"] = self.object.product
        return ctx


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Review
    template_name = "confirm_delete.html"

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse("product_detail", kwargs={"slug": self.object.product.slug})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_name"] = f"review of '{self.object.product.title}'"
        ctx["cancel_url"] = reverse("product_detail", kwargs={"slug": self.object.product.slug})
        return ctx
