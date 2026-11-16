from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # ვინახავთ ახალ მომხმარებელს ბაზაში
            return redirect('users:login')  # რეგისტრაციის მერე ვუშვებთ Login გვერდზე
    else:
        form = UserCreationForm()

    return render(request, 'users/register.html', {'form': form})
