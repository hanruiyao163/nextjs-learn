srs -> docker run --rm -it -p 1935:1935 -p 1985:1985 -p 8080:8080 -p 10080:10080/udp registry.cn-hangzhou.aliyuncs.com/ossrs/srs:5
srs -> docker run --rm -it -p 1935:1935 -p 1985:1985 -p 8080:8080 -p 10080:10080/udp registry.cn-hangzhou.aliyuncs.com/ossrs/srs:5 ./objs/srs -c conf/srt.conf



cd d:/outputs
ffmpeg -re -stream_loop -1 -i .\zoo.mp4 -c copy -f flv rtmp://localhost/live/zoo

# 老电脑wsl ip 172.25.94.112

zlmediakit -> docker run -id -p 1935:1935 -p 8080:80 -p 8443:443 -p 8554:554 -p 10000:10000 -p 10000:10000/udp -p 8000:8000/udp -p 9000:9000/udp zlmediakit/zlmediakit:master

ffmpeg -re -stream_loop -1 -i .\zoo.mp4  -f rtsp rtsp://127.0.0.1:8554/live/zoo




ffmpeg -f dshow -i video="Iriun Webcam" -c:v libx264 -preset ultrafast -tune zerolatency -f mpegts 'srt://127.0.0.1:10080?streamid=#!::r=live/livestream,m=publish'