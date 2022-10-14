#!/bin/bash
PLANET="-"
while [ $PLANET != "EXIT" ]
do
  echo -n "Enter the name of planet: "
  read PLANET
  if [ $PLANET != "EXIT" ]
  then
    echo -n "The $PLANET has "
    case $PLANET in
      Mercury | Venus ) echo -n "no";;
      Earth ) echo -n "one";;
      Mars ) echo -n "two";;
      Jupiter ) echo -n "79";;
      *) echo -n "an unknown number of";;
    esac
  echo " satellite(s)."
  fi
done


echo 'English'
echo 'Русский'
staticHash='578ce80c3b3dfa9ea84d6cd5735ed904 https://www.rbc.ru/society/'
dinamicHash='104e09942d322eb0a8299ce0244b7073'


echo 'End_'