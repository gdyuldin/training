# Trainig app exercises execution service

## Quick start

* Install Docker, docker-compose
* Run `docker-compose up -d`
* Check with `curl -i -X POST -H "Content-Type: application/json" -d '{"answer.py": "get_max = lambda x: x[0]"}' http://localhost:8000/exercises/example_python`

## Exercise check steps

1. Select exercise to check
2. Call `compose` method of exercise (to make temp workdir with all necessary files and user answer)
3. Build docker image to run exercise on it. Image building steps are cached in Docker, so it pretty fast
4. Create container from image
5. Send temp workdir (result of compose) to container `WORKDIR`
6. Start container and waiting for it stops
7. Get container exit code, stdout, stderr
8. Remove container, temp workdir
9. Return exit code, stdout, stderr

## Adding py.test exercises

1. Create new folder within `./exercises`
2. Create `README.md` with exercise description
3. Create `settings.py` and define some specific settings to exercise (if it need)
4. Create `test_smth.py` file with tests to answer code
5. Create your own `answer.py` within your exercise folder and fill it with your answer.py
6. Run `py.test exercises/your_exercise` to check that your checks works
7. Delete `answer.py` from your exercise folder

## Running inside docker


To run inside container we should get access to host docker.sock:

```bash
docker build -t trainig-app .
docker run -i -v /var/run/docker.sock:/var/run/docker.sock -v $(pwd):/opt/app --rm trainig-app
```


## Backend endpoints

### List of available exercises

Returns list of available exercises

<dl>
    <dt>Path</dt>
    <dd><code>/exercises</code></dd>
    <dt>Method</dt>
    <dd><code>GET</code></dd>
</dl>


Response example:
```json
{
    "exercises" :[
        {
            "name": "example_sh",
            "doc": "Markdown content with exercise description",
            "answers": ["desired_answer_files_names.sh"]
        }
    ]
}
```

### Check exercises

Check exercise and returns result

<dl>
    <dt>Path</dt>
    <dd><code>/exercises/&lt; name &gt;</code></dd>
    <dt>Method</dt>
    <dd><code>POST</code></dd>
</dl>

Request example:
```json
{"answer.sh": "ls -a | grep fuel"}
```

Response example:
```json
{
    "check_result": {
        "exit_code": 0,
        "stdout": "All tests passed",
        "stderr": ""
    }
}
```

## Testing

To run test you should have:

* Docker
* tox

Tests run with next command:

```bash
$ tox
```
