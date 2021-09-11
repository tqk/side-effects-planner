FROM aiplanning/planutils:latest

#maintainer information
LABEL maintainer="Anonymous"

# update the apt package manager
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN apt-get update && apt-get -y install locales

# install common packages
RUN apt-get install -y \
        build-essential \
        vim \
        git \
        gringo

# Set up the planning required
RUN planutils install -f downward
RUN planutils install -f lama-first
RUN planutils install -f lama
RUN planutils install -f tarski
RUN planutils install -f planning.domains


# default command to execute when container starts
CMD /bin/bash
