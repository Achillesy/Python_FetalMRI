from django.db import models

# Create your models here.
class track(models.Model):
    PseudoAcc = models.CharField(max_length=6)
    PseudoID = models.TextField()
    PseudoName = models.TextField()
    OrigAcc = models.TextField()
    OrigMR = models.TextField()
    OrigName = models.TextField()
    OrigGA = models.TextField()
    State = models.IntegerField()

    def __str__(self):
        return self.PseudoAcc + ":" + self.OrigMR + "." + self.OrigAcc

class series(models.Model):
    PseudoAcc = models.CharField(max_length=6)
    SeriesID = models.TextField()
    SeriesNumber = models.IntegerField()
    SeriesBrief = models.TextField()
    SeriesDescription = models.TextField()
    AcquisitionMatrix = models.TextField()
    Rows = models.IntegerField()
    Columns = models.IntegerField()
    PixelSpacing = models.TextField()
    Height = models.IntegerField()
    Width = models.IntegerField()
    State = models.IntegerField()

    def __str__(self):
        return self.PseudoAcc + ":" + self.SeriesBrief
