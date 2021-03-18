from django.db import models

# Create your models here.
class track(models.Model):
    PseudoAcc = models.TextField()
    PseudoID = models.TextField()
    PseudoName = models.TextField()
    OrigAcc = models.TextField()
    OrigMR = models.TextField()
    OrigName = models.TextField()
    OrigGA = models.TextField()
    State = models.IntegerField()

    def __str__(self):
        return self.PseudoAcc + ":" + self.OrigMR + "." + self.OrigAcc
