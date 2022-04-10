from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile,Post,Rating
from django.forms.widgets import Textarea


class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user



class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('photo', 'title', 'url', 'description', 'technologies_used',)
        
class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['design', 'usability', 'content']    


class UpdateUserForm(forms.ModelForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email')


class UpdateUserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'profile_pic', 'bio', 'phone_number']
        
        widgets = {
            'bio': Textarea(attrs={'cols': 20, 'rows': 5}),
        }

