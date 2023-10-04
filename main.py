# cloud function

def save_data_to_bigquery(request):
    from google.cloud import bigquery
    from datetime import datetime, timedelta
    client = bigquery.Client()
    project_id = 'project-pcsc-dt'
    dataset_id = 'vehicle_tracker'
    table_id = 'data_table'
    table_full_id = f'{project_id}.{dataset_id}.{table_id}'
    request_json = request.get_json(silent=True)
    if request_json:
        username = request_json['username']
        route = request_json['route']
        start_loc = request_json['start_loc']
        start_loc = datetime.strptime(start_loc, '%Y-%m-%d %H:%M:%S')
        end_loc = request_json['end_loc']
        end_loc = datetime.strptime(end_loc, '%Y-%m-%d %H:%M:%S')
        rows = [{'username': username, 'route': route, 'start_loc': start_loc.strftime('%Y-%m-%d %H:%M:%S'), 'end_loc': end_loc.strftime('%Y-%m-%d %H:%M:%S')}]
        errors = client.insert_rows_json(table_full_id, rows)  # Make an API request.
        if not errors:
            return "New rows have been added."
        else:
            return "Encountered errors while inserting rows: {}".format(errors)
    # return f'{username}, {lat}, {lon}, {date}'
