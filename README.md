# Backend for bash

### Run
```bash
cp .env.example .env
make run
```

### Roadmap
* fix for ^D on baskend
* improve quality of exceptions
* add tests

# TODO:
* Think about [custom PS1](https://bash-prompt-generator.org/)
  * PS1='\[\e[38;5;160m\]\h@\u:\[\e[38;5;33m\]\w\[\e[0m\] \[\e[38;5;160m\]->\[\e[0m\] '
  * PS1='\[\e[38;5;160m\]\h@\u:\[\e[38;5;33m\]\w\[\e[38;5;160m\]\$\[\e[0m\] '