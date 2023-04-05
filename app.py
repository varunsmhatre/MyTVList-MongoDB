from flask import Flask, render_template, request, redirect, url_for
from db_ops import db
import imdb

app = Flask(__name__)

username = 'varun'

def get_movie_list(col_name, col_value):
    data_list =  list(db.userdata.aggregate([
      { '$match': { f'movie_list.{col_name}': col_value } },
      {
        '$project': {
          'movie_list': {
            '$filter': {
              'input': '$movie_list',
              'as': 'movie_list',
              'cond': { '$eq': [f'$$movie_list.{col_name}', col_value] },
            },
          },
          '_id': 0,
        },
      },
    ]))

    if data_list:
        return data_list[0].get('movie_list')
    return []

@app.route("/")
@app.route("/watching")
def watching():
    type = 'watching'
    update_type = 'watched'
    data_list = get_movie_list('state', type)
    # data_list = list(data)[0].get('movie_list')
    columns = ['Title', 'Poster', 'Update!']
    # print(data_list)
    return render_template('watching.html', data_list=data_list, columns=columns, update_list=[update_type, update_type.capitalize()])

@app.route("/watched")
def watched():
    type = 'watched'
    data_list = get_movie_list('state', type)
    # data_list = list(data)[0].get('movie_list')
    columns = ['Title', 'Poster']
    return render_template('watched.html', data_list=data_list, columns=columns)
    # return render_template('watched.html', items=items, columns=columns)

@app.route("/watch_later")
def watch_later():
    type = 'watch_later'
    update_type = 'watching'
    data_list = get_movie_list('state', type)
    # data_list = list(data)[0].get('movie_list')
    columns = ['Title', 'Poster', 'Update!']
    # print(data_list)
    return render_template('watch_later.html', data_list=data_list, columns=columns, update_list=[update_type, update_type.capitalize()])

@app.route("/search", methods=['POST'])
def search():
    search_param = request.form.to_dict().get('search')
    ia = imdb.IMDb()
    items = ia.search_movie(search_param)
    data_list = []
    for item in items:
        data_dict = {'title':item.data.get('title'), 'poster':item.data.get('cover url'), 'movie_id':item.getID()}
        data_list.append(data_dict)        
    return render_template('search.html', title='search', data_list=data_list, columns=['Title', 'Poster'])

def get_movie_details(movie_id):
    ia = imdb.IMDb()    
    # searching the Id
    search = ia.get_movie(movie_id)
    return {'title':search.data.get('title'), 'poster':search.data.get('cover url') }


def edit_append_movie(movie_id, movie_status):
    movie_list = get_movie_list('movie_id', movie_id)
    if movie_list:
        # update
        print('update')
        db.userdata.update_one(
           { 'username' : username, "movie_list.movie_id": movie_id },
           { "$set": { "movie_list.$.state" : movie_status } }
        )
    else:
        # insert
        print('insert')
        details_dict = get_movie_details(movie_id)
        details_dict['movie_id'] = movie_id
        details_dict['state'] = movie_status
        print(details_dict)
        db.userdata.update_one({'username':username}, {'$push':{'movie_list':details_dict}})
        print('insert completed')

@app.route("/add_update/<string:add_type>")
def add_update_movie(add_type):
    print(add_type)
    print(request.args.get('movie_id'))
    edit_append_movie(request.args.get('movie_id'), add_type)
    return redirect(url_for(add_type))


@app.route("/about")
def about():
    return render_template('about.html', title='About')

if __name__ == '__main__':
    app.run(debug=True)
