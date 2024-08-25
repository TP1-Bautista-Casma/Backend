from django.db import models

class ColorblindImage(models.Model):
    TYPE_CHOICES = [
        ('anomalous_trichromatic', 'Tricromático Anómalo'),
        ('dichromatic', 'Dicromático'),
        ('achromatic', 'Acromático'),
    ]

    SUBTYPE_CHOICES = [
        ('protanomalous', 'Protanomalous'),
        ('deuteranomalous', 'Deuteranomalous'),
        ('tritanomalous', 'Tritanomalous'),
        ('protanopia', 'Protanopia'),
        ('deuteranopia', 'Deuteranopia'),
        ('tritanopia', 'Tritanopia'),
    ]

    image = models.ImageField(upload_to='colorblind_images/')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    subtype = models.CharField(max_length=50, choices=SUBTYPE_CHOICES, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.uploaded_at}"