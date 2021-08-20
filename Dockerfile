FROM aiplanning/planutils:latest

#maintainer information
LABEL maintainer="Christian Muise (christian.muise@queensu.ca)"

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

RUN pip3 install tarski

# Set up the planning required
RUN planutils install -f downward
RUN planutils install -f lama-first
RUN planutils install -f lama


# default command to execute when container starts
CMD /bin/bash
