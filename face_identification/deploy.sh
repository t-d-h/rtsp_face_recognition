#!/bin/bash

set -e

UNIXTIME=latest

IMAGE=rg.hoantran.me/rtsp_face_recognition/face_identification:$UNIXTIME

sudo docker build -t $IMAGE . && sudo docker push $IMAGE

echo $IMAGE


ssh hoantd-k0 kubectl rollout restart daemonset -n products face-identification

sleep 10

ssh hoantd-k0 kubectl get pods -n products -o wide
