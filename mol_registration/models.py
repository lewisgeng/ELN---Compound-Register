from django.db import models

# Create your models here.
class mol_props(models.Model):
    compound_id = models.CharField(max_length=50,unique=True, primary_key=True)
    smiles = models.CharField(max_length=1000)
    mol_file = models.TextField()
    mol_file_path = models.CharField(max_length=500)
    MW = models.FloatField()
    xlogp = models.FloatField()
    TPSA = models.FloatField()
    img_file = models.CharField(max_length=500)
    fingerprint = models.TextField(default='')
    lastest_reg_time = models.DateField(null=True,auto_now_add=True)


class cutome_fields_data(models.Model):
    compound = models.ForeignKey(to=mol_props,to_field="compound_id",on_delete=models.CASCADE,related_name = "compound_custom")
    #compound_id = models.CharField(max_length=50)
    batch_id = models.CharField(max_length=50)
    project = models.CharField(max_length=100)
    registrar = models.CharField(max_length=50, blank=True)
    from_supplier = models.CharField(max_length=100,blank=True)
    supplier_ref = models.CharField(max_length=100,blank=True)
    registration_time = models.DateTimeField(blank=True)
    salt = models.CharField(max_length=50)
    stoich =  models.FloatField(blank=True)
    location = models.CharField(max_length=100)
    weight = models.FloatField()
    weight_unit = models.CharField(max_length=50)
    appearance = models.CharField(max_length=50)
    chiral = models.CharField(max_length=50)
    comments = models.TextField()

class cutome_fields_dictionary(models.Model):
    field_name = models.CharField(max_length=100)
    field_value = models.CharField(max_length=100)



