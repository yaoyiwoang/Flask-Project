from routes import app

@app.route('/create_article.html')
def creat_article():
    return 'Create Ariticle'