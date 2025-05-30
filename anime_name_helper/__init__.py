# 注册自定义API路由
try:
    from .routes import register_routes
    def setup(app):
        register_routes(app)
except ImportError:
    pass 