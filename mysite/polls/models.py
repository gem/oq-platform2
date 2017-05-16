from django.db import models


class Recipe(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()


class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe)
    description = models.CharField(max_length=255)


class Instruction(models.Model):
    recipe = models.ForeignKey(Recipe)
    number = models.PositiveSmallIntegerField()
    description = models.TextField()
