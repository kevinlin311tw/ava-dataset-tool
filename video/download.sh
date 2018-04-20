ava_url="https://s3.amazonaws.com/ava-dataset/trainval/"

while read p; do
  echo $p
  echo $ava_url$p -O;
  curl $ava_url$p -O;
done <ava_file_names_trainval.txt


#for i in 0{1..9} {10..17};
#do
#        curl $ava_url"nturgbd_rgb_s0"$i".zip" -O; 
#done;

