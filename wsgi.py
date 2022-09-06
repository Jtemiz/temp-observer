from app.factory import create_app

application = create_app('app.config.BaseConfig')
if __name__ == '__main__':
	application.run(host='192.168.3.10', port=80)
