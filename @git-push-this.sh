## OPTIONAL # init
wsl --user root
git init

## on SURFACE
git add .
git commit -m ""

## OPTIONAL # git remote add origin https://github.com/hippomatter/iAmSmartGate-PoC.git
## OPTIONAL # git branch -M main

git remote set-url origin git@github.com:hippomatter/iAmSmartGate-PoC.git
ssh -T git@github.com

git push -u origin main

## OPTIONAL # clear cached
git rm -r --cached .
