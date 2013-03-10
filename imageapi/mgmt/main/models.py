from django.db import models


class Page(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.CharField(max_length=100, null=False, blank=True)
    suffix = models.CharField(max_length=100, null=False, blank=True)
    prefix = models.CharField(max_length=100, null=False, blank=True)
    
    def __unicode__(self):
        return "Page: %s" % self.name


class Placeholder(models.Model):
    width = models.IntegerField(default=100, null=False, blank=False)
    height = models.IntegerField(default=100, null=False, blank=False)
    text = models.CharField(max_length=100, null=False, blank=True)
    description = models.CharField(max_length=100, null=False, blank=True)
    page = models.ForeignKey("Page")
    # title = models.CharField(null=False, blank=True)
    # color
    # text size
    
    @property
    def label(self):
        label = "%s%s%s" % (self.page.prefix, self.text, self.page.suffix)
        return label or self.size

    @property
    def size(self):
        return "%sx%s" % (self.width, self.height)

    def __unicode__(self):
        return "Placeholder: %sx%s '%s'" % (self.width, self.height, self.text)

