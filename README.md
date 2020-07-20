# Sheetgo Backend Test

This repository was created in order to answer a test proposed to me by [Sheetgo](https://www.sheetgo.com/).

requirements:

1. [python3.8](http://https://www.python.org/ "1. python3.8")
2. [pipenv](https://pipenv.pypa.io/en/latest/ "2. pipenv")

## Instructions:

### Setup:

    $ git clone git@github.com:DiegoMagg/sheetgobackendtest.git .
    $ pipenv install

Add the JWT encryption key to the SEC_KEY environment variable in the .env file and run

    $ pipenv run flask init-db && pipenv run flask create-user <YOUR_EMAIL>

### Starting application and CURL testing:

    $ pipenv run flask run

Excel info:

    $ curl http://localhost:5000/api/excel/info/ -H "Authorization: Bearer $(pipenv run python3 generate_jwt.py <YOUR_EMAIL>)" -F file=@sample.xlsx

Image conversion:

    $ curl http://localhost:5000/api/image/convert/ -H "Authorization: Bearer $(pipenv run python3 generate_jwt.py <YOUR_EMAIL>)" -F file=@sheetgo.bmp --form format=<jpg or png> --output "<filename.SELECTED_FORMAT>"

Dropbox image conversion:

    $ curl http://localhost:5000/api/convert/fromdropbox/ \
      -H "authorization: Bearer $(pipenv run python3 generate_jwt.py <YOUR_EMAIL>)" \
      -H "content-type: application/json" \
      -d '{
    	"format": "<jpeg or png>",
    	"dropbox_token": "<DROPBOX_TOKEN>",
    	"path": "<DROPBOX_PATH>"
    }' \
    --output "<FILENAME.SELECTED_FORMAT>"

### Unit Testing:

    $ pipenv run python3 tests.py

With coverage report:

    $ pipenv install --dev
    $ pipenv run ./coverage_run.sh

**Note: To test the dropbox conversion api, it's necessary to set the dropbox environment variables in the .env file or these tests will be skipped.**

DROPBOX_PATH="/path/to/image.bmp"
DROPBOX_INVALID_FILE_PATH="/path/to/non-image.xlsx"

#### File Samples

- .xlsx file sample taken from [file-examples](https://file-examples.com/index.php/sample-documents-download/sample-xls-download/)
- Sheetgo logo taken from [here](https://images.saasworthy.com/sheetgo_2819_logo_1576503526_npwzg.png) (converted to BMP)
