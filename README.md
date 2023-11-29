# ToDo API

#### demo-project

#### * Project in dev now. Therefore, there may be errors in it

### Stack:
* Python
  * aiohttp
  * SQLAlchemy
  * pytest
* Redis - to store sessions
* Docker - project is too raw to use it, but later it will use to run app
* OpenAPI - for [API documentation](docs/api.yaml)

### Description:

Simple API. Users can log in and out. Authorized users can create, view,
edit, and delete their tasks. Tasks are stored in the database, and 
sessions are stored in Redis.