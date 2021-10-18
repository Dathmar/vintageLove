from django.shortcuts import render
from .models import UserFolders

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
