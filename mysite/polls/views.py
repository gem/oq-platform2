from django.http import HttpResponseRedirect
from django.views.generic import CreateView

from .forms import IngredientFormSet, InstructionFormSet, RecipeForm
from .models import Recipe

from django.views.generic.list import ListView
from django.utils import timezone



class RecipeCreateView(CreateView):
    template_name = 'polls/recipe_add.html'
    model = Recipe
    form_class = RecipeForm
    success_url = 'polls/success/'

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        ingredient_form = IngredientFormSet()
        instruction_form = InstructionFormSet()
        return self.render_to_response(
            self.get_context_data(form=form,
                                  ingredient_form=ingredient_form,
                                  instruction_form=instruction_form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        ingredient_form = IngredientFormSet(self.request.POST)
        instruction_form = InstructionFormSet(self.request.POST)
        if (form.is_valid() and ingredient_form.is_valid() and
            instruction_form.is_valid()):
            return self.form_valid(form, ingredient_form, instruction_form)
        else:
            return self.form_invalid(form, ingredient_form, instruction_form)

    def form_valid(self, form, ingredient_form, instruction_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        self.object = form.save()
        ingredient_form.instance = self.object
        ingredient_form.save()
        instruction_form.instance = self.object
        instruction_form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, ingredient_form, instruction_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form,
                                  ingredient_form=ingredient_form,
                                  instruction_form=instruction_form))

class RecipeListView(ListView):

    model = Recipe

    def get_context_data(self, **kwargs):
        context = super(RecipeListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
