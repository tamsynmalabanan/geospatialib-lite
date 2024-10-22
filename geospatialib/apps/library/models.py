from django.contrib.gis.db import models

from urllib.parse import urlparse

from . import choices

from ..utils.general import form_helpers

class MetaAbstractModel(models.Model):
    added_by = models.ForeignKey("main.User", verbose_name='Added by', on_delete=models.DO_NOTHING, related_name='%(class)ss_added')
    added_on = models.DateTimeField('Added on', auto_now_add=True)
    updated_by = models.ForeignKey("main.User", verbose_name='Updated by', on_delete=models.DO_NOTHING, blank=True, null=True, related_name='%(class)ss_updated')
    updated_on = models.DateTimeField('Updated on', auto_now=True)

    class Meta:
        abstract = True

class URL(MetaAbstractModel):
    path = models.URLField('URL', max_length=256, unique=True)

    @property
    def domain(self):
        return urlparse(self.path).netloc

class Dataset(MetaAbstractModel):
    url = models.ForeignKey("library.URL", verbose_name='URL', on_delete=models.CASCADE)
    format = models.CharField('Format', max_length=16, choices=form_helpers.dict_to_choices(choices.DATASET_FORMATS))
    name = models.CharField('Layer', max_length=256)