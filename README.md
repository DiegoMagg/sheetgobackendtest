# Sheetgo Backend Test

This repository was created in order to answer a test proposed to me by [Sheetgo](https://www.sheetgo.com/).

requirements:
1. [python3.8](http://https://www.python.org/ "1. python3.8")
2. [pipenv](https://pipenv.pypa.io/en/latest/ "2. pipenv")


## Instructions:

### Setup:

    $ git clone git@github.com:DiegoMagg/sheetgobackendtest.git .
    $ pipenv install
    $ pipenv run flask init-db && pipenv run flask create-user <YOUR_EMAIL>


### Starting application and CURL testing:
Add the JWT encryption key to the SEC_KEY environment variable in the .env file and run
```
$ pipenv run flask run
```
Excel info:

    $ curl http://localhost:5000/api/excel/info/ -H 'Authorization: Bearer <APPLICATION_TOKEN>' -F file=@sample.xlsx
Image conversion:

    $ curl http://localhost:5000/api/image/convert/ -H 'Authorization: Bearer <APPLICATION_TOKEN>' -F file=@sheetgo.bmp --form format=<jpg or png> --output "<filename.SELECTED_FORMAT>"
Dropbox image conversion:

    $ curl http://localhost:5000/api/image/convert/fromdropbox/ \
    -H 'authorization: Bearer <APPLICATION_TOKEN>' \
    -H 'content-type: application/json' \
    -d '{
    "format": "<jpeg or png>",
    "dropbox_token": "<DROPBOX_TOKEN>",
    "path": "<DROPBOX_FILE_PATH>"
    }' \
    --output "<filename.SELECTED_FORMAT>"


Change APPLICATION_TOKEN for one above

### Accepted tokens:

 - lucas@sheetgo.com:
   `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6Imx1Y2FzQHNoZWV0Z28uY29tIn0.UQ12G2FqritLFWIcpSYTJyLPnvcPukf9EBl4mGy9d0w`
 - mauricio@sheetgo.com:
   `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6Im1hdXJpY2lvQHNoZWV0Z28uY29tIn0.gYbFJ_dQEGy50O5ILzxUEFDgui4GjNMxFOXonyZFE5I`
 - rafael@sheetgo.com:
   `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InJhZmFlbEBzaGVldGdvLmNvbSJ9.mPTcpDxQnGeS35X1o_ViqCLnMKaChO5sI2LvLEYtLPA`

### Unit Testing:

    $ pipenv run python3 tests.py
With coverage report:

    $ pipenv install --dev
    $ pipenv run ./coverage_run.sh


**Note: To test the dropbox conversion api, it's necessary to set the dropbox environment variables in the .env file or these tests will be skipped.**
#### File Samples

 - .xlsx file sample taken from  [file-examples](https://file-examples.com/index.php/sample-documents-download/sample-xls-download/)

 - Sheetgo logo taken from   [here](https://images.saasworthy.com/sheetgo_2819_logo_1576503526_npwzg.png) (converted to BMP)
