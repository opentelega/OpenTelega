from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

from fileserver.HashCalc import HashSumType, hashsum_of_file
from fileserver.HashCalc import get_salted_password

class Option(models.Model):
    name = models.CharField(
        blank=True, null=True, max_length=64, unique=True)
    value = models.CharField(blank=True, null=True, max_length=512)
    is_accessible = models.BooleanField(default=True)

    def __str__(self):
        return "Name: {}, Value: {}".format(self.name, self.value)

class User(models.Model):
    username = models.CharField(blank=True, null=True, max_length=64)
    hashed_pass = models.CharField(blank=True, null=True, max_length=64)
    salt = models.CharField(blank=True, null=True, max_length=64)

    def __str__(self):
        if (self.username):
            return self.username
        else:
            return "None"

    def CheckPassword(self, password):
        return (self.hashed_pass == get_salted_password(self.salt, password))

def getFileLastId():
    try:
        return str(File.objects.latest('id').id + 1)
    except Exception:
        return '1'

def get_upload_path(instance, filename):
    return getFileLastId()
    
class File(models.Model):
    recipients = models.ManyToManyField(User, related_name="file_recipients")
    sender = models.ForeignKey(User, on_delete=models.CASCADE,
        related_name="file_sender", null=True)
    format = models.CharField(max_length=256, blank=True)
    hash_sum = models.CharField(max_length=128, blank=True)
    hash_alg = models.IntegerField(default=7)
    date_of_creating = models.DateTimeField(auto_now=True)
    uploaded_file = models.FileField(upload_to=get_upload_path)

    def __str__(self):
        try:
            fields = ("ID", "From", "To", "Size", "Hash", "Uploaded Date")
            values = (self.id, self.sender, self.get_recipients(),
                self.get_file_size(), self.hash_sum[:10], \
                self.date_of_creating)

            return ", ".join('{}: {}'.format(*t) for t in zip(fields, values))
        except Exception:
            return "Could not generate string for file with id {}".format(\
                self.id)

    def get_recipients(self):
        try:
            return ", ".join(map(lambda x: x[0], \
                self.recipients.all().distinct().values_list("username")))
        except Exception:
            return "Couldn't get recipient list"

    def get_file_size(self):
        try:
            return self.uploaded_file.size
        except Exception:
            return "Couldn't get file size"

@receiver(pre_save, sender = File)
def post_save_file(sender,  instance, *args, **kwargs):
    f = instance.uploaded_file
    f.open()
    instance.hash_sum = hashsum_of_file(HashSumType(instance.hash_alg), 
        instance.uploaded_file)

@receiver(post_delete, sender=File)
def file_post_delete_handler(sender, **kwargs):
    try:
        f = kwargs['instance']
        storage, path = f.uploaded_file.storage, f.uploaded_file.path
        storage.delete(path)
    except Exception:
        pass