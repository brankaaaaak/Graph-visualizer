from django.db import models

# Create your models here.
class Node:
    def __init__(self, id):
        self._id = id
        self._edges = []
        self._attributes = {}
