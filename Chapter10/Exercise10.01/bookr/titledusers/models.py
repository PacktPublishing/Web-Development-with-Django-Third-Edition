from django.db import models
from django.contrib.auth.models import User

class TitledUser(User):
    class Meta:
        verbose_name = _('titled user')
        verbose_name_plural = _('titled users')

    class TitleChoices(models.TextChoices):
        PROF = "PROF", "Prof"
        DR = "DR", "Dr"

    class HonorificChoices(models.TextChoices):
        MR = "MR", "Mr"
        MISS = "MISS", "Miss"
        MRS = "MRS", "Mrs"
        MS = "MS", "MS"

    title = models.CharField(verbose_name="Title",
            blank=True, choices=TitleChoices.choices)
    honorific = models.CharField(verbose_name="Honorific",
            blank=True, choices=HonorificChoices.choices)

    def get_full_name(self):
        if self.title:
            return f'{self.title} {self.firstname} {self.secondname}'
        elif self.honorific:
            return f'{self.honorific} {self.firstname} {self.secondname}'
        else:
            return f'{self.firstname} {self.secondname}'
