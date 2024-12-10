from dash_views import create_delivery_dash
from dash_views import create_driver_dash
from dash_views import create_main_dash

def init_dash_apps(server):
    # Dash 앱 통합
    delivery_dash = create_delivery_dash(server)
    driver_dash = create_driver_dash(server)
    main_dash = create_main_dash(server)
    return {"delivery": delivery_dash, "driver": driver_dash, "main": main_dash}
