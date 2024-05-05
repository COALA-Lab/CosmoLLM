#!/bin/bash


rm -rf dist

mkdir -p dist/cosmollm
cp -r DEBIAN dist/cosmollm

mkdir -p dist/cosmollm/usr/bin
cp cosmollm dist/cosmollm/usr/bin

cd dist/cosmollm || exit
git clone https://github.com/COALA-Lab/CosmoLLM.git cosmollm --recursive
mkdir opt
mv cosmollm opt

cd ../
fakeroot dpkg-deb --build cosmollm
