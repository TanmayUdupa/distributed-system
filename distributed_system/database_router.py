class DatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'users':
            return 'users'
        elif model._meta.app_label == 'products':
            return 'products'
        elif model._meta.app_label == 'orders':
            return 'orders'
        return None

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'users':
            return db == 'users'
        elif app_label == 'products':
            return db == 'products'
        elif app_label == 'orders':
            return db == 'orders'
        return None
