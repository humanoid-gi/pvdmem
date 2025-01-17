

docker build --progress=plain --network=host -t pvdmem_app:v0.1 .
docker run -d --network=host --restart always pvdmem_app:v0.1