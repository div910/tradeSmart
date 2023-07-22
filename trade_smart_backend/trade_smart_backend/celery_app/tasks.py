from trade_smart_backend.celery_app.apps import app

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))