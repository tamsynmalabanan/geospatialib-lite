from django.db import models
from django.contrib.gis.db import models as gis_models

from urllib.parse import urlparse

from . import choices

from ..utils.general import form_helpers

class URL(models.Model):
    path = models.URLField('URL', max_length=256, unique=True)

    @property
    def domain(self):
        return urlparse(self.path).netloc

class Dataset(gis_models.Model):
    url = models.ForeignKey("library.URL", verbose_name='URL', on_delete=models.CASCADE)
    format = models.CharField('Format', max_length=16, choices=form_helpers.dict_to_choices(choices.DATASET_FORMATS))
    name = models.CharField('Layer', max_length=256)