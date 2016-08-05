### Trainig app exercises execution service

#### Running inside docker

```bash
docker build -t trainig-app .
docker run -i -v /var/run/docker.sock:/var/run/docker.sock -v $(pwd):/opt/app --rm trainig-app
```
