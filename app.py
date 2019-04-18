from flask import Flask, request, make_response, redirect, url_for, render_template
import requests
import json

app = Flask(__name__)

@app.route('/')
def index():
	cookie_id = request.cookies.get('uid')
	cookie_csrftoken = request.cookies.get('csrftoken')

	if cookie_id is None or cookie_csrftoken is None:
		resp = make_response(render_template('reg_form.html'))
		return resp # Вернуть форму для введения логина и пароля
		
	return redirect(url_for('books'))# Редирект на страницу со списком книг

@app.route('/login', methods = ['POST'])
def login():
	email = request.form['email']
	password = request.form['psw']
	resp = requests.post("https://mybook.ru/api/auth/", json = {'email':email, 'password':password})
	cookies = {}
	cookies['csrftoken'] = resp.cookies['csrftoken']
	cookies['session'] = resp.cookies['session']
	cookies['uid'] = resp.cookies['uid']
	resp = make_response(redirect('/books'))

	for key, value in cookies.items():
		resp.set_cookie(key, value)

	return resp

@app.route('/books')
def books():
	books ={}
	while True:
		headers = {'Accept': 'application/json; version=5'}
		path = "/api/bookuserlist/"
		resp = requests.get('https://mybook.ru' + path, headers = headers, cookies = request.cookies)
		resp_json = resp.content.decode('utf8').replace("'", '"')
		data = json.loads(resp_json)

		for book in data['objects']:
			books[book['book']['name']] = (book['book']['authors_names'],
										  ('https://mybook.ru/storage/public/' + book['book']['default_cover']))

		if data['meta']['next'] == None:
			break

		path = data['meta']['next']

	return render_template('books.jinja2', books = books)

if __name__ == '__main__':
	app.run(debug=True)
