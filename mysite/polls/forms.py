from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from .models import Recipe, Ingredient, Instruction


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ['title','description']


IngredientFormSet = inlineformset_factory(Recipe, Ingredient, fields = ['description'])
InstructionFormSet = inlineformset_factory(Recipe, Instruction, fields = ['number', 'description'])
