### Trainig app exercises execution service

#### Exercise check steps

1. Select exercise to check
2. Call `compose` method of exercise (to make temp workdir with all necessary files and user answer)
3. Build docker image to run exercise on it. Image building steps are cached in Docker, so it pretty fast
4. Create container from image
5. Send temp workdir (result of compose) to container `WORKDIR`
6. Start container and waiting for it stops
7. Get container exit code, stdout, stderr
8. Remove container, temp workdir
9. Return exit code, stdout, stderr

#### Adding py.test exercises

1. Create new folder within `./exercises`
2. Create `README.md` with exercise description
3. Create `prepare.py` with `compose` function - this will prepare worspace for answer check
4. Create `test_smth.py` file with tests to answer code
5. Create your own `answer.py` within your exercise folder and fill it with your answer.py
6. Run `py.test exercises/your_exercise` to check that your checks works
7. Delete `answer.py` from your exercise folder

#### Running inside docker


To run inside container we should get access to host docker.sock:

```bash
docker build -t trainig-app .
docker run -i -v /var/run/docker.sock:/var/run/docker.sock -v $(pwd):/opt/app --rm trainig-app
```
