""" CELERY APP"""
from __future__ import absolute_import, unicode_literals
import os
import sys
from os.path import dirname

proj_name = "trade_smart_backend"
root_path = dirname(dirname(dirname(dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.abspath(os.path.join(root_path, proj_name)))
sys.path.insert(0, os.path.abspath(os.path.join(root_path, proj_name, proj_name)))
sys.path.insert(0, os.path.abspath(os.path.join(root_path, proj_name, proj_name, 'apps')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trade_smart_backend.settings')

from trade_smart_backend.celery_app.apps import app