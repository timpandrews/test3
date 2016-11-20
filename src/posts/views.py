from urllib import quote_plus

from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from posts.forms import PostForm
from posts.models import Post

def post_list(request):
    today = timezone.now().date()
    if request.user.is_staff or request.user.is_superuser:
        qs_list = Post.objects.all().order_by("-id")
    else:
        #qs_list = Post.objects.filter(draft=False).filter(publish__lte=timezone.now()).order_by("-id")
        qs_list = Post.objects.active()

    query = request.GET.get("query")
    if query:
        qs_list = qs_list.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        ).distinct()

    paginator = Paginator(qs_list, 2) # Show 25 contacts per page
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        qs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        qs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        qs = paginator.page(paginator.num_pages)

    context = {
        "object_list": qs,
        "title": "Posts",
        "page_request_var": page_request_var,
        "today": today,
    }
    return render(request, "post_list.html", context)

def post_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    if not request.user.is_authenticated():
        raise Http404

    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        messages.success(request, "Success: New Record Added")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "form": form,
    }
    return render(request, "post_form.html", context)

def post_detail(request, slug=None):
    instance = get_object_or_404(Post, slug=slug)
    if instance.draft or instance.publish > timezone.now().date():
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404
    share_string = quote_plus(instance.content)
    context = {
        "title": "detail",
        "post": instance,
        "share_string": share_string,
    }
    return render(request, "post_detail.html", context)

def post_update(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404

    instance = get_object_or_404(Post, slug=slug)

    form = PostForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Success: Records Updated", extra_tags="whatever")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "title": "detail",
        "post": instance,
        "form": form,
    }
    return render(request, "post_form.html", context)

def post_delete(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug=slug)
    instance.delete()
    messages.success(request, "Success: Record Deleted")
    return redirect("posts:list")

