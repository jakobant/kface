## kface
Flask app for face recognition. Created to run local with a
Magic Mirror project

## Intro
Simple webservice for face recognition. Does have dependency
for redis

## Usage

Start with docker-compose
```
docker-compose up
```

#Add Obama to the database

![Image of Obama](https://github.com/jakobant/kface/raw/master/test/obama.jpeg)
```
curl -XPOST -Fname='Barak Obama' -Ffile=@test/obama.jpg localhost/upload
```

#Check if Obama i know from the Obama and Biden image

![Image of Obama and Biden](https://github.com/jakobant/kface/raw/master/test/obamaandbiden.jpg)
```
curl -XPOST -Ffile=@test/obamaandbiden.jpg localhost/who2
return:
{
  "locations": [
    [
      167,
      408,
      322,
      253
    ],
    [
      116,
      683,
      270,
      528
    ]
  ],
  "names": [
    "Unknown",
    "Barak Obama"
  ],
  "upload_file": "cc47c84cdc5c4c5084bf4c8f4eacfef5.jpg"
}
```

Or simply visit the local http://localhost to upload some image to check

![Image of Obama known](https://github.com/jakobant/kface/raw/master/test/obamaknown.jpg)

## Api path
Quick overview, POST

#### /upload
Upload a image to the face_recognition database
Parameters :
- name, text used a identifier name.  If not specified the filename is use.
- file, a file to upload

Example
```curl
curl -XPOST -Fname='Barak Obama' -Ffile=@test/obama.jpg localhost/upload
```

#### /who
Upload a image for face_recognition.

Paremeters :
- file, a file to upload
Example
```curl
curl -XPOST -Fname='Barak Obama' -Ffile=@test/obama.jpg localhost/who
```

return:
```
{
  "locations": [
    [
      167,
      408,
      322,
      253
    ],
    [
      116,
      683,
      270,
      528
    ]
  ],
  "names": [
    "Unknown",
    "Barak Obama"
  ],
  "upload_file": "cc47c84cdc5c4c5084bf4c8f4eacfef5.jpg"
}
```

#### /who2
Same as above, except the image rotation detection is not applied

#### /who3
Same as above, excpet upload image does get the faces and names drawn.

