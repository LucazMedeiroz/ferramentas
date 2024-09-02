from django.db import models

# Create your models here.
# models.py

from django.db import models

class HelpTopicLabelMapping(models.Model):
    help_topic_id = models.IntegerField(unique=True)
    label_id = models.IntegerField()

    class Meta:
        verbose_name = "Help Topic Label Mapping"
        verbose_name_plural = "Help Topic Label Mappings"

    def __str__(self):
        return f"Help Topic ID: {self.help_topic_id}, Label ID: {self.label_id}"


    


    