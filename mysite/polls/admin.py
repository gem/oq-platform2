from django.contrib import admin

from .models import Recipe, Ingredient, Instruction 


class InstructionInline(admin.StackedInline):
    model = Instruction
    extra = 3


class IngredientInline(admin.StackedInline):
    model = Ingredient
    extra = 3

class RecipeAdmin(admin.ModelAdmin):
    # fieldsets = [
    #     (None,               {'fields': ['question_text']}),
    #     ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    # ]
    inlines = [IngredientInline, InstructionInline]

admin.site.register(Recipe, RecipeAdmin)
