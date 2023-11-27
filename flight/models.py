from django.db import models
from django.contrib.auth.models import User

class hero_area(models.Model):
    hero_background_banner = models.ImageField(upload_to='hero_area')

    def __str__(self):
        return 'Banner Image'
    
class forget_password_token(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    forget_password_token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
class TokenInfo(models.Model):
    token = models.CharField(max_length=1000)
    last_generation_date = models.DateField()
    def __str__(self):
        return f"Last Generation Date: {self.last_generation_date}"

class Markup(models.Model):
    markup_percentage = models.FloatField()

    def __str__(self):
        return str(self.markup_percentage)
    
class Our_Most_Popular_Tour(models.Model):
    badge_discount = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(upload_to='Our_Most_Popular_Tours')
    tour_category = models.CharField(max_length=15, null=True, blank=True)
    no_of_tour_place = models.CharField(max_length=50, null=True, blank=True)
    title = models.CharField(max_length=200)
    loaction = models.CharField(max_length=200)
    tour_duration = models.CharField(max_length=200)
    price = models.IntegerField()

    def __str__(self):
        return self.title

class Our_Best_Deal(models.Model):
    image = models.ImageField(upload_to='Our_Best_Deal')
    from_and_to = models.CharField(max_length=10, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    price = models.CharField(max_length=200, null=True, blank=True)
    Mobile_Number = models.CharField(max_length=15, null=True, blank=True, help_text="+911234567890 No. in this formate")

    def __str__(self):
        return self.from_and_to
    
class Video_section(models.Model):
    thumbnail_image = models.ImageField(upload_to='Video_section')
    youtube_link = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return 'Video section'
    
class partner_logo(models.Model):
    logo_image = models.ImageField(upload_to='partner_logo')

    def __str__(self):
        return 'Partner Logo'
    
class testimonial(models.Model):
    client_image = models.ImageField(upload_to='testimonial')
    client_name = models.CharField(max_length=50, null=True, blank=True)
    client_type = models.CharField(max_length=50, null=True, blank=True)
    client_description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.client_name
    
class Blog(models.Model):
    blog_image = models.ImageField(upload_to='blog')
    posted_by = models.CharField(max_length=200, null=True, blank=True)
    posted_at = models.DateField()
    blog_title = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.blog_title
    