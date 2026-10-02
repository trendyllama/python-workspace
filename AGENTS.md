

# Tools

- This project uses Docker

# building the project

- `docker build --tag python-test --file Dockerfile .`

# Running the project

- `docker run --name my-python-container --detach --rm python-test`
- `docker exec --tty --interactive my-python-container sh`