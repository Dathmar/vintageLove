from django.shortcuts import render, get_object_or_404
from .models import UserFolders, FolderContents
from products.models import Product


# Create your views here.
def folder_list(request):
    if request.user.is_authenticated:
        folders = UserFolders.objects.filter(user=request.user)
        context = {
            'folders': folders,
        }
        return render(request, 'folder-list.html', context)
    else:
        return render(request, 'registration/login.html')


def folder_view(request, folder_slug, user_id=''):
    if request.user.is_authenticated:
        folder = get_object_or_404(UserFolders, user=request.user, slug=folder_slug)
        folder_contents = FolderContents.objects.filter(folder=folder)

        suggested_items = Product.objects.filter(status__available_to_sell=True)[:3]

        context = {
            'folder': folder,
            'folder_contents': folder_contents,
            'suggested_items': suggested_items,
        }

        return render(request, 'folder-contents.html', context)
    else:
        pass
