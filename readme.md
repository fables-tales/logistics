# Logistics

Logistics is an isolated service for exporting student robotics robot.zip files.

## Developer Setup

* Make sure you have the python tool `virtualenv` installed
* run `./script/setup`
* run `source venv/bin/activate` (this puts you in an isolated python
  environment, run `deactivate` to quit it)
* run the tests with `./script/test`
* run the app with `python app.py`

## API Spec (0.1.0)

### POST `/export`

Accepts the following parameters:

* `git_url`: the url of the repository to clone

Responds differently based on the HTTP accept header delivered by the client.
Always responds with an access control allow origin header, such that this
endpoint can be used in a browser from any domain.

### When the client specifies `Accept: text/html`

Redirects back to "/" with some session state held server side to render
different responses and eventually redirect the user to the zip file.

### When the client specifies `Accept: application/json`

If the repository specified by `git_url` was clonable then a status code of
`200` is given and a JSON object with a single property `zip_url` is returned
with a path to the zip.

An example response is:

```
{"zip_url": "/static/zips/efcc521b-79e7-483c-82a9-2207cde168c8/robot.zip"}
```
If the repository specified by `git_url` was not clonable then a status code
of `400` is given and a JSON object with the property `errors` is returned.
`errors` is an array, which as of this version (0.1.0), contains a string value
"EXPORT_FAIL".

### When the client specifies any other Accept header

Behaviour is unspecified and should not be relied upon.
