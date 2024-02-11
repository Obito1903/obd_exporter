#!/bin/sh

sudo rfcomm --auth connect 0 C1:0B:64:26:37:2F 2 &
sleep 5
.venv/bin/python main.py
