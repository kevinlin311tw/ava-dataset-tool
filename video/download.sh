ava_url="https://s3.amazonaws.com/ava-dataset/trainval/"

while read p; do
  echo $p
  echo $ava_url$p -O;
  curl $ava_url$p -O;
done <ava_file_names_trainval.txt

