from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(basedir, "base.sqlite")

db = SQLAlchemy(app)
ma = Marshmallow(app)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    prix = db.Column(db.Float, nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    categorie_id = db.Column(db.Integer, db.ForeignKey('categorie.id'), nullable=False)

    def __init__(self, nom,description, prix, quantite, categorie_id):
        self.nom = nom
        self.description = description
        self.prix = prix
        self.quantite = quantite
        self.categorie_id = categorie_id


class Categorie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
   

    def __init__(self, nom, description):
        self.nom = nom
        self.description = description



class ArticleSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nom', 'description', 'prix', 'quantite', 'categorie_id')

article_schema = ArticleSchema()
articles_schema = ArticleSchema(many=True)

class CategorieSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nom', 'description')

categorie_schema = CategorieSchema()
categories_schema = CategorieSchema(many=True)




with app.app_context():
    db.create_all()
    print('Database created')


@app.route('/articles', methods=['GET'])
def get_articles():
    all_articles = Article.query.all()
    result = articles_schema.dump(all_articles)
    return jsonify(result)


@app.route('/articles/<id>', methods=['GET'])
def get_article(id):
    article = Article.query.get(id)
    return article_schema.jsonify(article)


@app.route('/articles', methods=['POST'])
def add_article():
    nom = request.json.get('nom')
    description = request.json.get('description')
    prix = request.json.get('prix')
    quantite = request.json.get('quantite')
    categorie_id = request.json.get('categorie_id')

    new_article = Article(nom=nom, description=description, prix=prix, quantite=quantite, categorie_id=categorie_id)
    db.session.add(new_article)
    try:
        db.session.commit()
        return article_schema.jsonify(new_article), 201
    except IntegrityError:
        db.session.rollback()
        return article_schema.jsonify({'message': 'Erreur: cet article existe déjà.'}), 409


@app.route('/articles/<int:id>', methods=['PUT'])
def update_article(id):
    article = Article.query.get(id)
    if article:
        nom = request.json.get('nom')
        description = request.json.get('description')
        prix = request.json.get('prix')
        quantite = request.json.get('quantite')
        categorie_id = request.json.get('categorie_id')

        article.nom = nom
        article.description = description
        article.prix = prix
        article.quantite = quantite
        article.categorie_id = categorie_id

        db.session.commit()


        return article_schema.jsonify(article)
    else:
        return article_schema.jsonify({'message': 'Article non trouvé.'}), 404


@app.route('/articles/<int:id>', methods=['DELETE'])
def delete_article(id):
    article = Article.query.get(id)
    if article:
        db.session.delete(article)
        db.session.commit()

        return article_schema.jsonify(article)
    else:
        return article_schema.jsonify({'message': 'Article non trouvé.'}), 404


@app.route('/categories', methods=['GET'])
def get_categories():
    all_categories = Categorie.query.all()
    result = categories_schema.dump(all_categories)
    return jsonify(result)


@app.route('/categories/<int:id>', methods=['GET'])
def get_categorie(id):
    categorie = Categorie.query.get(id)
    return categorie_schema.jsonify(categorie)


@app.route('/categories', methods=['POST'])
def add_categorie():
    nom = request.json.get('nom')
    description = request.json.get('description')

    new_categorie = Categorie(nom=nom, description=description)
    db.session.add(new_categorie)
    db.session.commit()
    return categorie_schema.jsonify(new_categorie)


@app.route('/categories/<int:id>', methods=['PUT'])
def update_categorie(id):
    categorie = Categorie.query.get(id)
    if categorie:
        nom = request.json.get('nom')
        description = request.json.get('description')

        categorie.nom = nom
        categorie.description = description

        db.session.commit()

        return categorie_schema.jsonify(categorie)
    else:
        return categorie_schema.jsonify({'message': 'Categorie non trouvée.'}), 404


@app.route('/categories/<int:id>', methods=['DELETE'])
def delete_categorie(id):
    categorie = Categorie.query.get(id)
    if categorie:
        db.session.delete(categorie)
        db.session.commit()

        return categorie_schema.jsonify(categorie)
    else:
        return categorie_schema.jsonify({'message': 'Categorie non trouvée.'}), 404


if __name__ == "__main__":
    app.run(debug=True)
