from django.db import models

class Room(models.Model):
    code = models.CharField(max_length=10, unique=True, db_index=True)
    impostor_count = models.PositiveSmallIntegerField(default=1)
    reveal_index = models.PositiveSmallIntegerField(default=0)
    starter_name = models.CharField(max_length=64, null=True, blank=True)

    # fjala e raundit
    word = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

class Player(models.Model):
    room = models.ForeignKey(Room, related_name="players", on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    is_impostor = models.BooleanField(default=False)

    class Meta:
        unique_together = ("room", "name")

class Word(models.Model):
    text = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.text
