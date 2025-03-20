from setup import createApp



if __name__ == '__main__':
    app = createApp()
   
    app.run(host='localhost', port=3000, debug=True)