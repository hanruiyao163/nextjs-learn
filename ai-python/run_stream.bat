docker run --rm -it -p 1935:1935 -p 1985:1985 -p 8080:8080 registry.cn-hangzhou.aliyuncs.com/ossrs/srs:5
ffmpeg -re -stream_loop -1 -i .\zoo.mp4 -c copy -f flv rtmp://localhost/live/zoo