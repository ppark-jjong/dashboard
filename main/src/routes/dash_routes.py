from dash import Input, Output
from src.data.redis_client import get_rider_data, get_delivery_data  # Redis 클라이언트
from src.data.bigquery_client import query_bigquery_data  # BigQuery 클라이언트
from dash_views.layouts import create_delivery_layout, create_driver_layout


def register_dash_callbacks(app):
    @app.callback(
        Output("delivery-table", "data"),
        Input("delivery-search-input", "value")
    )
    def update_delivery_table(search_value):
        # Redis에서 데이터를 가져와 Dash에 표시
        data = get_delivery_data()
        if search_value:
            data = [row for row in data if search_value.lower() in str(row).lower()]
        return data

    @app.callback(
        Output("driver-table", "data"),
        Input("driver-search-input", "value")
    )
    def update_driver_table(search_value):
        # BigQuery에서 데이터를 가져와 Dash에 표시
        data = query_bigquery_data("SELECT * FROM drivers")
        if search_value:
            data = [row for row in data if search_value.lower() in str(row).lower()]
        return data
