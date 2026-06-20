from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("products/search/", views.product_search, name="product_search"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("category/<slug:slug>/", views.category_detail, name="category_detail"),
    path("shops/<slug:slug>/", views.shop_detail, name="shop_detail"),
    # Shop management (authenticated users with a shop)
    path("my-shop/create/", views.ShopCreateView.as_view(), name="shop_create"),
    path("my-shop/edit/", views.ShopUpdateView.as_view(), name="shop_edit"),
    path("my-shop/delete/", views.ShopDeleteView.as_view(), name="shop_delete"),
    path("my-shop/products/new/", views.ProductCreateView.as_view(), name="product_create"),
    path("my-shop/products/<slug:slug>/edit/", views.ProductUpdateView.as_view(), name="product_edit"),
    path("my-shop/products/<slug:slug>/delete/", views.ProductDeleteView.as_view(), name="product_delete"),
    # Staff-only category management
    path("staff/categories/new/", views.CategoryCreateView.as_view(), name="category_create"),
    path("staff/categories/<slug:slug>/edit/", views.CategoryUpdateView.as_view(), name="category_edit"),
]
