# Recommender RESTful API Document

## Introduction

This is a recommender system for `chinese articles`.

 - Structure diagram

    ![](https://storage.googleapis.com/cocas/structure_diagram.png)

 - Doc2Vec & Web crawler
    It uses python package `BeautifulSoup` to crawl thousands of medical articles from websites as training set of Doc2vec. It ueses `gensim`, python package for nature language process, to implement Doc2Vec model training which can convert string to high dimensions vector. Before converting articles, it has to uese `jieba` to segment chinese sentence to words first.

    So core function of this app is to computing similarity between articles, building a similarity matrix and implementing a recommender system.

 - Flask and gunicorn

    It uses `Flask` framework and run by `gunicorn` including some flask plugins, `Flask-Login` as login system , `flask_restplus` as utils of restful API, `Flask-SQLAlchemy` as ORM.

 - Oauth2.0

    It follows client credentals of OAuth2.0 for security, and using `Authlib` to implement.

 - SQL and noSQL Database

    It store user, client, token, article and similarity matrix info in `mysql`. It caches recommend list and vectors of articles in `redis` to speed up.

 - Celery

    When computing similarity matrix of huge number of articles, app is facing huge time consuming, so app ueses `Celery` to compute similarity matrix in background and set up periodic tasks.

    Because of the asynchronous tasks, article appears in recommend list after computing task done.

 - Docker

    It has four containers to run, flask + gunicorn, mysql, redis, Celery. It uses `docker-compose` to manage containers.


## Clone with git

    git clone https://gitlab.com/lucas860529/recommender.git

## Run the app

    docker-compose up --build

## Initialize the app
 - database
    `docker-compose exec api recommender init_db --with-testdb`

- seed account
 `docker-compose exec api recommender create_seed`

 - loading default articles
## Run the tests

    docker-compose exec api py.test recommender/test

## APIs

[Create an new account](#1-1)

[Log in account](#1-2)

[Log out account](#1-3)

[Get auth token](#1-4)

[Get articles](#1-5)

[Create an new article](#1-6)

[update an article](#1-7)

[Delete an article](#1-8)

[Recommend articles by plain text](1-#9)

[Recommend articles by ID](#1-10)

[Compute similarty between two articles](#1-11)

[Re-compute similarity cache](#1-12)

[General error response](#1-13)


# REST API

The REST API to the Recommender is described below.

<span id="1-1"></span>
## CREATE AN NEW ACCOUNT

### Request

`POST /user/signup`

### Description
Sign up an new account. Log in Automatically after signing up.

Note: Only admin can sign up an new admin account.

### Parameters

Field | Description
------|------------
email | Pass your email as identity. `required`
password | Pass string. `required`
role | Choose `admin` or `member`. Default is `member`
username | Pass your nick name.

#### Example
    {
        "username": "Luacs",
        "password": "LucasPassword",
        "role": "admin",
        "email": "Lucas@gmail.com"
    }


### Response

    {
        "code": 200,
        "message": "ok",
        "payLoad": {
            "client_id": "id string",
            "client_secret": "secret string"
        }
    }

###ERROR
    
    {
        "code": 400,
        "message": "This email is already used. Please try another one"
    }

    
    {
        "code": 400,
        "message": "Only accept admin or member in role parameter "
    }
    

<span id="1-2"></span>
## LOG IN

### Request

`POST /user/login`

### Description
Log in account.

### Parameters

Field | Description
------|------------
email | email as identity. `required`
password | Password. `required`


#### Example
    {
        "password": "LucasPassword",
        "email": "Lucas@gmail.com"
    }

### Response
    {
        "code": 200,
        "message": "ok",
        "payLoad": {
            "client_id": "id string",
            "client_secret": "secret string"
        }
    }
### ERRORS

    {
        "code": 400,
        "message": "wrong password or email"
    }
<span id="1-3"></span>
## LOG OUT

### Request

`POST /user/logout`

### Description
Log out account. 

`Log in required`

### Parameters

`None`


### Response

    {
        "code": 200,
        "message": "ok",
        "payLoad": "logout success"
    }
<span id="1-4"></span>
## GET OAUTH TOKEN

### Request

`GET /user/oauth/token`

### Description
Get token with `client secret` and `client id`, get both by loging in.

Note: set header `ContentType` :`application/x-www-form-urlencoded`

`log in required`

### Parameters


Field | Description
------|------------
grant_type | Only implement client_credentals `required`
client_id | Get client id by loging in.  `required`
client_secret | Get client secret by loging in. `required`

## Example

    {
        'client_id': 'CLIENT_ID',
        'client_secret': 'CLIENT_SECRET',
        'grant_type': 'client_credentals',
    }


### Response

    {
        "access_token": "token string",
        "expires_in": 864000,
        "token_type": "Bearer"
    }


<span id="1-5"></span>
## GET ARTICLES

### Request

`GET /article/page/{page}`

### Description

Get all articles with pagination.


`member auth required`

### Parameters

`None`

### Response

    {
        "code": 200,
        "message": "ok",
        "payLoad": [
            {
                "answer": "answer",
                "ask": "ask",
                "content": "content",
                "created_on": "Tue, 30 Jul 2019 09:57:49 GMT",
                "division": "division",
                "id": 1,
                "title": "test1",
                "type": "type",
                "updated_on": "Tue, 30 Jul 2019 09:57:49 GMT"
            },
            {
                "answer": "answer",
                "ask": "ask",
                "content": "content",
                "created_on": "Tue, 30 Jul 2019 09:57:49 GMT",
                "division": "division",
                "id": 2,
                "title": "test2",
                "type": "type",
                "updated_on": "Tue, 30 Jul 2019 09:57:49 GMT"
            },
            {
                "answer": "answer",
                "ask": "ask",
                "content": "content",
                "created_on": "Tue, 30 Jul 2019 09:57:49 GMT",
                "division": "division",
                "id": 3,
                "title": "test3",
                "type": "type",
                "updated_on": "Tue, 30 Jul 2019 09:57:49 GMT"
            }
        ]
    }

### ERRORS
    {
        "code": 404,
        "message": "The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again."
    }

<span id="1-6"></span>
## CREATE A NEW ARTICLE

### Request

`POST /article`

### Description

Define two types of medical articles. First is article with two field `ask` and `answer`, and ask is from patients and asnwer is from docters. The other only accepts `content` like regular articles.

Please choose either `ask` and `answer` or `content`, if you pass both app will only take the content.


`admin auth required`
### Parameters

Field | Description
------|------------
title | title of article `required`
ask | Ask field of the ask-answer type article.
answer | Answer field of the ask-answer type article.
content | Article content. If null, content will be filled with conbination of ask and answer as an article content.
division | division of the aritcle. `required`
type | type of the article. `required`

#### Example
    {
        "title": "title",
        "ask":"ask",
        "answer":"answer",
        "type":"type",
        "division":"division"
    }

### Response

    {
        "code": 200,
        "message": "ok",
        "payLoad": {
            "answer": "answer",
            "ask": "ask",
            "content": "content",
            "created_on": "Thu, 15 Aug 2019 08:12:53 GMT",
            "division": "division",
            "id": 1,
            "title": "title",
            "type": "type",
            "updated_on": "Thu, 15 Aug 2019 08:12:53 GMT"
        }
    }

### ERRORS

    {
        "code": 400,
        "message": "This title of article already exists"
    }

<span id="1-7"></span>
## UPDATE AN ARTICLE

### Request

`PATCH /article/{id}`

### Description
Edit fields of the article. 
Note: It is not allowed to edit `title`.

`admin auth required`
### Parameters

Field | Description
------|------------
ask | Ask field of the ask-answer type article.
answer | Answer field of the ask-answer type article.
content | Article content. If `ask` or `answer` is edited, it will be edited, too.
division | division of the aritcle.
type | type of the article.

### Example
    {
        "ask":"ask",
        "answer":"answer",
        "type":"type",
        "division":"division"
    }


### Response

    {
        "code": 200,
        "message": "ok",
        "payLoad": {
            "answer": "answer",
            "ask": "ask",
            "content": "content",
            "created_on": "Thu, 15 Aug 2019 08:12:53 GMT",
            "division": "division",
            "id": 1,
            "title": "title",
            "type": "type",
            "updated_on": "Thu, 15 Aug 2019 08:12:53 GMT"
        }
    }

### ERRORS
    {
        "code": 404,
        "message": "This id is invalid"
    }


<span id="1-8"></span>
## DELETE AN ARTICLE

### Request

`DELETE /article/{id}`

### Description
It will set `isDelete` field to 1. you can rollback the deletion in database if you want with developing reason.


`admin auth required`
### Parameters

`None`

### Response

    {
        "code": 200,
        "message": "ok",
        "payLoad": {
            "answer": "answer",
            "ask": "ask",
            "content": "content",
            "created_on": "Thu, 15 Aug 2019 08:12:53 GMT",
            "division": "division",
            "id": 1,
            "title": "title",
            "type": "type",
            "updated_on": "Thu, 15 Aug 2019 08:12:53 GMT"
        }
    }

### ERRORS

    {
        "code": 404,
        "message": "This article has been deleted"
    }

    {
        "code": 404,
        "message": "This id is invalid"
    }

## RECOMMEND ARTICLES BY PLAIN TEXT

### Request

`GET /article/recommend/text`


### Description

It will return recommend list of articles based on the text you pass in.



`member auth required`

### Parameters

Field | Description
------|------------
text | taget text to be computed similarity comparing with other aticles in database.  `required`
amount | `Integer`. Amount of article you want `required`


### Example

    URL?text=someText&amount=5
### Response

    {
        "code": 200,
        "message": "ok",
        "payLoad": [
            {
                "answer": "answer",
                "ask": "ask",
                "content": "content",
                "created_on": "Tue, 30 Jul 2019 09:57:49 GMT",
                "division": "division",
                "id": 1,
                "title": "test1",
                "type": "type",
                "updated_on": "Tue, 30 Jul 2019 09:57:49 GMT"
            },
            {
                "answer": "answer",
                "ask": "ask",
                "content": "content",
                "created_on": "Tue, 30 Jul 2019 09:57:49 GMT",
                "division": "division",
                "id": 2,
                "title": "test2",
                "type": "type",
                "updated_on": "Tue, 30 Jul 2019 09:57:49 GMT"
            },
            {
                "answer": "answer",
                "ask": "ask",
                "content": "content",
                "created_on": "Tue, 30 Jul 2019 09:57:49 GMT",
                "division": "division",
                "id": 3,
                "title": "test3",
                "type": "type",
                "updated_on": "Tue, 30 Jul 2019 09:57:49 GMT"
            }
        ]
    }


### ERRORS

    {
        "code": 400,
        "message": "amount is too large"
    }
## RECOMMEND ARTICLES BY ID

### Request

`GET /article/recommend/{id}`

### Description

After computing similarity matrix which is a periodic task in this app, app already caches the result of recommend list in redis. Users can get the result by this API without computing it again. It improves the time complexity while number of aticles is large.

But, if users request before computing matrix, it will pass the article content of id which user passes in to `RECOMMEND ARTICLES BY PLAIN TEXT`, and obviously it takes more time.

`member auth required`

### Parameters

Field | Description
------|------------
amount | `Integer`. Amount of article you want. `required`

#### Example

    URL?amount=5

### Response

    {
        "code": 200,
        "message": "ok",
        "payLoad": [
            {
                "answer": "answer",
                "ask": "ask",
                "content": "content",
                "created_on": "Tue, 30 Jul 2019 09:57:49 GMT",
                "division": "division",
                "id": 1,
                "title": "test1",
                "type": "type",
                "updated_on": "Tue, 30 Jul 2019 09:57:49 GMT"
            },
            {
                "answer": "answer",
                "ask": "ask",
                "content": "content",
                "created_on": "Tue, 30 Jul 2019 09:57:49 GMT",
                "division": "division",
                "id": 2,
                "title": "test2",
                "type": "type",
                "updated_on": "Tue, 30 Jul 2019 09:57:49 GMT"
            },
            {
                "answer": "answer",
                "ask": "ask",
                "content": "content",
                "created_on": "Tue, 30 Jul 2019 09:57:49 GMT",
                "division": "division",
                "id": 3,
                "title": "test3",
                "type": "type",
                "updated_on": "Tue, 30 Jul 2019 09:57:49 GMT"
            }
        ]
    }

### ERRORS

    {
        "code": 400,
        "message": "amount is too large"
    }


## COMPUTE SIMILARTY BETWEEN TWO ARTICLES

### Request

`GET /article/similarty`

### Description

To compute similarity between two string.

`log in required`
`member auth required`


### Parameters

Field | Description
------|------------
text1 | first target text. `required`
text2 | second target text. `required`



### Example
    URL/article/similarity?text1=sometext&text2=sometext

### Response

    {
        "code": 200,
        "message": "ok",
        "payLoad": {
            "similarity": 0.9999999999
        }
    }

## RE-COMPUTE SIMILARITY CACHE

### Request

`PATCH /article/cache`

### Description

As mentioned, re-cmopute cache is a periodic task, but you also can cache immediately by this API. It runs task in background by `Celery`.

Computing steps is following:

 - Check every article is refered to a vector and cache in the redis.
 - Compute similarity with other articles and cahce the `partial` result in redis.

Note: redis only cahces 15 most similar articles.

`admin auth required`


### Parameters

    None

### Response

    {
        "code": 200,
        "message": "ok",
        "payLoad": "ok"
    }

## GENERAL ERROR RESPONSE
    {
        "code": 500,
        "message": "The server encountered an internal error and was unable to complete your request.  Either the server is overloaded or there is an error in the application."
    }
