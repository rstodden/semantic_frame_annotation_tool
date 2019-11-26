from django.apps import AppConfig


class AnnotateConfig(AppConfig):
    name = 'annotate'

    # it just imports the signal file when the app is ready
    def ready(self):
        import annotate.signals
