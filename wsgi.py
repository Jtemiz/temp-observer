from app.factory import create_app

app = create_app('app.config.BaseConfig')

if __name__ == "__main__":
    app.run()
