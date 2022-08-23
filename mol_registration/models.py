from django.db import models

# Create your models here.
class mol_props(models.Model):
    compound_id = models.CharField(max_length=50)
    smiles = models.CharField(max_length=1000)
    mol = models.TextField()
    MW = models.FloatField()
    xlogp = models.FloatField()
    TPSA = models.FloatField()
    img_file = models.CharField(max_length=500)

