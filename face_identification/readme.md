to run locally:


pip install wheel setuptools pip --upgrade 
pip install git+https://github.com/ageitgey/face_recognition_models --verbose


flask server, nhan anh mat nguoi va tim xem day la ai


insert:
```
curl -X POST http://localhost:5000/insert -F "name=John Doe" -F "image=@/path/to/john_doe_photo1.jpg"

for image in $(ls -d hoan/*); do echo $image; curl -X POST http://localhost:5000/insert -F "name=Hoan" -F "image=@$image";  done
```
Luu y: insert thi anh chi co khuon  mat 1 nguoi thoi, 2 nguoi la sai, khong co mat nguoi cung sai

search:
```
curl -X POST http://localhost:5000/search -F "image=@hoan/anh2.jpg"
```

return:
```
{
  "matches": ["John Doe", "Alice", "Unknown"]
}
```

docker run test:
```
 sudo docker run --rm -e   MYSQL_PASSWORD= -p 5000:5000 rg.hoantran.me/rtsp_face_recognition/face_identification:latest
```
