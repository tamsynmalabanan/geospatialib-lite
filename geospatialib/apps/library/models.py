from django.db import models
from django.contrib.gis.db import models as gis_models

class Dataset(gis_models.Model):
    url = ''
    format = ''
    name = ''