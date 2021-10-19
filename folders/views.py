from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.db.models import ObjectDoesNotExist
from .models import UserFolders, FolderContents
from products.models import Product


def folder_not_found(request):
    return render(request, 'folder-not-found.html')


# Create your views here.
def folder_list(request):
    if request.user.is_authenticated:
        folders = UserFolders.objects.filter(user=request.user)
        context = {
            'folders': folders,
        }
        return render(request, 'folder-list.html', context)
    else:
        return redirect(reverse('login'))


def folder_view(request, folder_slug, user_name=False):
    if request.user.is_authenticated:
        if user_name and request.user.username.casefold() != user_name.casefold():
            try:
                folder = UserFolders.objects.get(user__username__iexact=user_name, slug__iexact=folder_slug)
            except ObjectDoesNotExist:
                folder = None

            if not folder or not folder.is_public:
                return redirect('folders:not-found')
        else:
            try:
                folder = UserFolders.objects.get(user=request.user, slug__iexact=folder_slug)
            except ObjectDoesNotExist:
                folder = None

        if not folder:
            return redirect('folders:not-found')

        folder_contents = FolderContents.objects.filter(folder=folder)

        suggested_items = Product.objects.filter(status__available_to_sell=True)[:3]

        context = {
            'folder': folder,
            'folder_contents': folder_contents,
            'suggested_items': suggested_items,
        }

        return render(request, 'folder-contents.html', context)
    else:
        return redirect(reverse('login'))
