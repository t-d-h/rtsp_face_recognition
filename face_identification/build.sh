#!/bin/bash

set -e

UNIXTIME=latest

IMAGE=rg.hoantran.me/rtsp_face_recognition/face_identification:$UNIXTIME

sudo docker build -t $IMAGE . && sudo docker push $IMAGE

echo $IMAGE



