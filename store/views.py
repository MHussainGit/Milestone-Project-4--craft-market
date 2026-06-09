from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import ProductForm, ShopForm
from .models import Category, Product, Shop


def home(request):
    featured = Product.objects.featured()[:8]
    categories = Category.objects.all()
    return render(request, "store/home.html", {"featured": featured, "categories": categories})


def product_list(request):
    products = Product.objects.in_stock().select_related("shop", "category")
    category_slug = request.GET.get("category")
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)
    categories = Category.objects.all()
    return render(request, "store/product_list.html", {
        "products": products,
        "categories": categories,
        "selected_category": selected_category,
    })


def product_search(request):
    query = request.GET.get("q", "").strip()
    products = []
    if query:
        products = (
            Product.objects.filter(title__icontains=query)
            | Product.objects.filter(shop__name__icontains=query)
        ).select_related("shop").distinct()
    return render(request, "store/product_search.html", {"products": products, "query": query})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.select_related("user").all()
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
    return render(request, "store/product_detail.html", {
        "product": product,
        "reviews": reviews,
        "user_review": user_review,
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category).select_related("shop")
    return render(request, "store/category_detail.html", {
        "category": category,
        "products": products,
    })


def shop_detail(request, slug):
    shop = get_object_or_404(Shop, slug=slug)
    products = shop.products.in_stock()
    return render(request, "store/shop_detail.html", {"shop": shop, "products": products})


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class ShopOwnerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """User must own a shop to access product management views."""

    def test_func(self):
        return hasattr(self.request.user, "shop")


class ProductOwnerOrStaffMixin(LoginRequiredMixin, UserPassesTestMixin):
    """For edit/delete: product must belong to the current user's shop, or user is staff."""

    def get_object(self, queryset=None):
        return get_object_or_404(Product, slug=self.kwargs["slug"])

    def test_func(self):
        product = self.get_object()
        return self.request.user.is_staff or (
            hasattr(self.request.user, "shop") and product.shop == self.request.user.shop
        )


class ProductCreateView(ShopOwnerRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "store/product_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["shop"] = self.request.user.shop
        return kwargs

    def form_valid(self, form):
        form.instance.shop = self.request.user.shop
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("product_detail", kwargs={"slug": self.object.slug})


class ProductUpdateView(ProductOwnerOrStaffMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "store/product_form.html"
    slug_url_kwarg = "slug"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["shop"] = self.object.shop
        return kwargs

    def get_success_url(self):
        return reverse("product_detail", kwargs={"slug": self.object.slug})


class ProductDeleteView(ProductOwnerOrStaffMixin, DeleteView):
    model = Product
    template_name = "confirm_delete.html"
    success_url = reverse_lazy("product_list")
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_name"] = str(self.object)
        ctx["cancel_url"] = reverse("product_detail", kwargs={"slug": self.object.slug})
        return ctx


class ShopCreateView(LoginRequiredMixin, CreateView):
    model = Shop
    form_class = ShopForm
    template_name = "store/shop_form.html"
    success_url = reverse_lazy("profile")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, "shop"):
            return redirect("shop_edit")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ShopUpdateView(LoginRequiredMixin, UpdateView):
    model = Shop
    form_class = ShopForm
    template_name = "store/shop_form.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return get_object_or_404(Shop, user=self.request.user)


class CategoryCreateView(StaffRequiredMixin, CreateView):
    model = Category
    template_name = "store/category_form.html"
    fields = ["name", "description"]
    success_url = reverse_lazy("product_list")


class CategoryUpdateView(StaffRequiredMixin, UpdateView):
    model = Category
    template_name = "store/category_form.html"
    fields = ["name", "description"]
    success_url = reverse_lazy("product_list")
