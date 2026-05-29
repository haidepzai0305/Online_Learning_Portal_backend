class DatabaseRouter:
    """
    A router to control all database operations on models in the
    various services.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'app':
            return 'default'
        if model._meta.app_label == 'courses_service_app':
            return 'courses'
        if model._meta.app_label == 'notification_service_app':
            return 'notifications'
        if model._meta.app_label == 'payment_service':
            return 'payments'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'app':
            return 'default'
        if model._meta.app_label == 'courses_service_app':
            return 'courses'
        if model._meta.app_label == 'notification_service_app':
            return 'notifications'
        if model._meta.app_label == 'payment_service':
            return 'payments'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'app':
            return db == 'default'
        if app_label == 'courses_service_app':
            return db == 'courses'
        if app_label == 'notification_service_app':
            return db == 'notifications'
        if app_label == 'payment_service':
            return db == 'payments'
        
        # Django internal apps
        if db in ['courses', 'payments', 'notifications']:
            return False
            
        return True
