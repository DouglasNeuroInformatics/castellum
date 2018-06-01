APP_LABEL = "subject_management"


class SubjectManagementRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == APP_LABEL:
            return APP_LABEL

    def db_for_write(self, model, **hints):
        if model._meta.app_label == APP_LABEL:
            return APP_LABEL

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == obj2._meta.app_label and obj1._meta.app_label == APP_LABEL:
            return True

    def allow_migrate(self, db, app_label, **hints):
        if db == APP_LABEL:
            return app_label == APP_LABEL
