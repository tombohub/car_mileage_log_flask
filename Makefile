flask:
	uv run flask --app car_mileage_log_flask.app run --debug

reload:
	browser-sync 'http://127.0.0.1:5000' --files .

gunicorn:
	gunicorn car_mileage_log_flask.app:app