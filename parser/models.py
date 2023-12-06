from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Card(models.Model):
    name = models.CharField(max_length=250, verbose_name='Имя')
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL")
    price = models.IntegerField(verbose_name='Цена')
    link = models.CharField(max_length=400, verbose_name='Ссылка')
    photo = models.ImageField(upload_to="photos", verbose_name="Фото", blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        indexes = [
            models.Index(fields=['slug'])
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Card.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('', kwargs={'card_slug': self.slug})
