from django.shortcuts import render
from django.utils import timezone
from django.template import RequestContext

# Create your views here.

def simple_view(request):
	today = timezone.now()
	data_dictionary = {'today': today}
	my_template = 'hackathon_app/user_interface.html'
	return render(request,my_template,{'today':today},context_instance=RequestContext(request))


 
	

