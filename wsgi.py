from app.factory import create_app

application = create_app('app.config.BaseConfig')
if __name__ == '__main__':
	application.run(host='localhost', port=5000)
